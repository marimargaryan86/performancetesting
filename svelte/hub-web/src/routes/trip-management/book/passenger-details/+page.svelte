<script lang="ts" context="module">
  function getDefaultPassengers(passengers: PassengerCountData): PassengerData[] {
    return [
      ...Array(passengers.adults)
        .fill(undefined)
        .map<PassengerData>(() => ({ document: {}, type: "adult" })),
      ...Array(passengers.children)
        .fill(undefined)
        .map<PassengerData>(() => ({ document: {}, type: "child" })),
      ...Array(passengers.infants)
        .fill(undefined)
        .map<PassengerData>(() => ({ document: {}, type: "infant" })),
    ];
  }
</script>

<script lang="ts">
  import { browser } from "$app/environment";
  import { page } from "$app/stores";
  import type { MaybePromise } from "@sveltejs/kit";
  import Button from "components/ui/button.svelte";
  import type { OfferPriceQuoteModel } from "models/booking/offer";
  import routeConfig from "routeConfig";
  import { onDestroy } from "svelte";
  import { callAction, sleep } from "utils/common";
  import Countdown from "../countdown.svelte";
  import Summary from "../summary/summary.svelte";
  import Passengers, { type PassengerData } from "./passengers.svelte";
  import ContactInformation, { type ContactInformationData } from "./contact-information.svelte";
  import { goto } from "$app/navigation";
  import type { PassengerCountData, ResolvedSearchData } from "../common";
  import { URLExtended } from "utils/url";

  export let data;

  let getPriceQuoteTask: MaybePromise<OfferPriceQuoteModel | undefined> = data.priceQuote;
  let priceQuoteId: string | undefined = data.priceQuote.id;
  let bookingDetails: { passengers: PassengerData[]; contactInformation: ContactInformationData } =
    {
      passengers: getDefaultPassengers(data.searchData.passengers),
      contactInformation: {
        phone: {},
        address: {},
      },
    };

  $: backUrl = getBackUrl(data.searchData);
  $: priceQuoteId = data.priceQuote.id;
  $: if (browser && priceQuoteId) {
    getPriceQuoteTask = pollPriceQuote(priceQuoteId);
  }

  function getBackUrl(searchData: ResolvedSearchData): URL {
    return new URLExtended(routeConfig.tripManagement.book.select.root, {
      base: $page.url.origin,
      query: {
        origin: searchData.origin.id,
        destination: searchData.destination.id,
        adults: searchData.passengers.adults,
        children: searchData.passengers.children,
        infants: searchData.passengers.infants,
        outbound: searchData.departureAfter.toLocaleDateString("sv-SE"),
      },
    });
  }

  async function pollPriceQuote(id: string): Promise<OfferPriceQuoteModel | undefined> {
    if (priceQuoteId !== id) {
      return undefined;
    }

    if (data.priceQuote.status === "completed") {
      return data.priceQuote;
    }

    const result = await callAction<{ priceQuote: OfferPriceQuoteModel }>({
      action: routeConfig.tripManagement.book.payment.actions.poll,
      apply: false,
    });

    if (result.type !== "success") {
      return undefined;
    }

    if (
      result.data?.priceQuote.status === "unspecified" ||
      result.data?.priceQuote.status === "failed"
    ) {
      return undefined;
    }

    if (result.data?.priceQuote.status === "completed") {
      return result.data.priceQuote;
    }

    await sleep(2000);

    return pollPriceQuote(id);
  }

  async function goToNext(): Promise<void> {
    if (!data.priceQuote.price) {
      return;
    }

    const result = await callAction({
      action: routeConfig.tripManagement.book.passengerDetails.actions.createOrder,
      data: {
        priceQuoteId: data.priceQuote.id,
        passengers: bookingDetails.passengers,
        contact: bookingDetails.contactInformation,
        price: data.priceQuote.price,
      },
      dataType: "json",
      apply: false,
    });

    if (result.type !== "success") {
      return;
    }

    goto(routeConfig.tripManagement.book.confirmation.root);
  }

  onDestroy(() => {
    priceQuoteId = undefined;
  });
</script>

<svelte:head>
  <title>Passenger details · Book · Junction Hub</title>
</svelte:head>

<div class="content">
  {#await getPriceQuoteTask then}
    <Countdown expiresAt={data.priceQuote.expiresAt} show />
  {/await}

  <div class="scroll">
    <div class="details">
      <Passengers bind:passengers={bookingDetails.passengers} />

      <ContactInformation
        countries={data.countries}
        bind:contactInformation={bookingDetails.contactInformation}
      />
    </div>

    <Summary
      passengers={data.searchData.passengers}
      offer={data.priceQuote.offer}
      options={data.priceQuote.options}
    />
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button size="small" variant="text" href={backUrl.toString()}>Previous</Button>
    <Button size="small" on:click={goToNext}><span class="next-btn">Next</span></Button>
  </div>
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    width: 100%;
    padding-top: 24px;
    overflow: auto;
  }

  .content > :global(.countdown) {
    max-width: 1104px;
    margin: 0 24px 24px;
  }

  .scroll {
    --summary-width: 320px;
    --passengers-width: calc(1152px - var(--summary-width) - 72px);

    display: flex;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    padding: 0 24px 24px;
    overflow: auto;
  }

  .scroll > .details {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-self: flex-start;
    width: 100%;
    max-width: var(--passengers-width);
  }

  .scroll > :global(.summary) {
    position: sticky;
    top: 0;
    left: 0;
    flex-shrink: 0;
    width: var(--summary-width);
  }

  .actions {
    position: relative;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    gap: 16px;
    justify-content: space-between;
    width: 100%;
    max-width: 1104px;
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .actions > .wrapper > :global(button) {
    width: 140px;
  }
</style>
