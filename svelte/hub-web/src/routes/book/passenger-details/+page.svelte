<script lang="ts" context="module">
  function getDefaultPassengers(passengers: PassengerCountModel): PassengerData[] {
    return [
      ...Array<PassengerData>(passengers.adults).fill({ document: {}, type: "adult" }),
      ...Array<PassengerData>(passengers.children).fill({ document: {}, type: "child" }),
      ...Array<PassengerData>(passengers.infants).fill({ document: {}, type: "infant" }),
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
  import Summary from "./summary.svelte";
  import Passengers, { type PassengerData } from "./passengers.svelte";
  import ContactInformation, { type ContactInformationData } from "./contact-information.svelte";
  import type { PassengerCountModel } from "../common";
  import { goto } from "$app/navigation";

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

  function getBackUrl(searchData: typeof data.searchData): URL {
    const url = new URL(routeConfig.book.select.root, $page.url.origin);
    url.searchParams.set("origin", searchData.origin.id);
    url.searchParams.set("destination", searchData.destination.id);
    url.searchParams.set("adults", searchData.passengers.adults.toString());
    url.searchParams.set("children", searchData.passengers.children.toString());
    url.searchParams.set("infants", searchData.passengers.infants.toString());
    url.searchParams.set("outbound", searchData.departureAfter.toLocaleDateString("sv-SE"));

    return url;
  }

  async function pollPriceQuote(id: string): Promise<OfferPriceQuoteModel | undefined> {
    if (priceQuoteId !== id) {
      return undefined;
    }

    const result = await callAction<{ priceQuote: OfferPriceQuoteModel }>({
      action: routeConfig.book.passengerDetails.actions.poll,
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

  function goToNext(): void {
    goto(routeConfig.book.payment.root);
  }

  onDestroy(() => {
    priceQuoteId = undefined;
  });
</script>

<svelte:head>
  <title>Summary · Book · Junction Hub</title>
</svelte:head>

<div class="content">
  <Countdown expiresAt={data.priceQuote.expiresAt} show />

  <div class="scroll">
    {#await getPriceQuoteTask then priceQuote}
      {JSON.stringify(priceQuote)}
    {/await}

    <div class="details">
      <Passengers bind:passengers={bookingDetails.passengers} />

      <ContactInformation
        countries={data.countries}
        bind:contactInformation={bookingDetails.contactInformation}
      />
    </div>

    <Summary passengers={bookingDetails.passengers} />
  </div>
</div>

<div class="actions">
  <Button size="small" variant="outline" href={backUrl.toString()}>Previous</Button>
  <Button size="small" on:click={goToNext}><span class="next-btn">Next</span></Button>
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
    display: flex;
    gap: 16px;
    justify-content: space-between;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
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

  .actions > :global(button) {
    width: 140px;
  }
</style>
