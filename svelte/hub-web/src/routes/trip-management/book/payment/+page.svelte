<script lang="ts" context="module">
  function getDefaultPassengers(passengers: PassengerCountData): PartialPassengerData[] {
    return [
      ...Array(passengers.adults)
        .fill(undefined)
        .map<PartialPassengerData>(() => ({ document: {}, type: "adult" })),
      ...Array(passengers.children)
        .fill(undefined)
        .map<PartialPassengerData>(() => ({ document: {}, type: "child" })),
      ...Array(passengers.infants)
        .fill(undefined)
        .map<PartialPassengerData>(() => ({ document: {}, type: "infant" })),
    ];
  }
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import { URLExtended } from "utils/url.js";
  import Payment from "./payment.svelte";
  import PassengerEntry, {
    getPassengerValidator,
    type PartialPassengerData,
  } from "./passenger-entry.svelte";
  import ContactInformation, {
    contactInformationData,
    type PartialContactInformationData,
  } from "./contact-information.svelte";
  import Countdown from "../countdown.svelte";
  import { z } from "zod";
  import type { PassengerCountData } from "../common";
  import { pendableCall } from "utils/pendable-call";
  import { callAction } from "utils/common";
  import { goto } from "$app/navigation";

  export let data;

  let payment: Payment | undefined;
  let bookingData: {
    passengers: PartialPassengerData[];
    contactInformation: PartialContactInformationData;
  } = {
    passengers: getDefaultPassengers(data.searchData.passengers),
    contactInformation: { phone: {}, address: {} },
  };
  let errors: z.ZodFormattedError<z.infer<typeof bookingDetailsValidator>> | undefined = undefined;

  $: bookingDetailsValidator = z.object({
    passengers: z.array(getPassengerValidator(data.priceQuote.required)),
    contactInformation: contactInformationData,
  });
  $: backUrl = getBackUrl(data.searchData);

  function getBackUrl(searchData: typeof data.searchData): URL {
    return new URLExtended(routeConfig.tripManagement.book.select.root, {
      base: $page.url.origin,
      query: {
        origin: searchData.origin.id,
        destination: searchData.destination.id,
        adults: searchData.passengers.adults.toString(),
        children: searchData.passengers.children.toString(),
        infants: searchData.passengers.infants.toString(),
        outbound: searchData.departureAfter.toLocaleDateString("sv-SE"),
      },
    });
  }

  async function createOrder(): Promise<boolean> {
    errors = undefined;
    const validationResult = bookingDetailsValidator.safeParse(bookingData);

    if (!validationResult.success) {
      errors = validationResult.error.format();

      return false;
    }

    const result = await callAction({
      action: routeConfig.tripManagement.book.payment.actions.createOrder,
      data: {
        priceQuoteId: data.priceQuote.id,
        passengers: validationResult.data.passengers,
        contact: validationResult.data.contactInformation,
        price: data.priceQuote.price,
      },
      dataType: "json",
      apply: false,
    });

    if (result.type !== "success") {
      return false;
    }

    return true;
  }

  const { pending, func: pay } = pendableCall(async () => {
    if (!payment) {
      return;
    }

    if (!(await payment.pay())) {
      return;
    }

    if (data.searchData.paymentIntent) {
      data.searchData.paymentIntent.confirmed = true;
    }

    if (!(await createOrder())) {
      return;
    }

    await goto(routeConfig.tripManagement.book.confirmation.root);
  });
</script>

<svelte:head>
  <title>Payment · Book · Trip Management · Junction Hub</title>
</svelte:head>

<div class="content">
  <Countdown expiresAt={data.priceQuote.expiresAt} show />

  <div class="wrapper">
    <div class="column passengers">
      {#each bookingData.passengers as passenger, idx}
        <PassengerEntry
          bind:passenger
          errors={errors?.passengers?.[idx]}
          required={data.priceQuote.required}
          passengerNumber={idx + 1}
        />
      {/each}
    </div>

    <div class="column payment">
      <ContactInformation
        countries={data.countries}
        bind:contactInformation={bookingData.contactInformation}
        errors={errors?.contactInformation}
      />

      <Payment bind:this={payment} priceQuote={data.priceQuote} searchData={data.searchData} />
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button size="small" variant="text" href={backUrl.toString()}>Previous</Button>
    <Button size="small" on:click={pay}>
      Next

      {#if $pending}
        <LoadingIcon />
      {/if}
    </Button>
  </div>
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    height: 100%;
    padding: 24px;
    overflow: auto;
  }

  .content > :global(.countdown) {
    max-width: 1104px;
  }

  .wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    max-width: 1104px;
    height: 100%;
    overflow: auto;
  }

  .column {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    overflow: auto;
  }

  .column.passengers {
    min-width: 648px;
  }

  .column.payment {
    min-width: 432px;
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
