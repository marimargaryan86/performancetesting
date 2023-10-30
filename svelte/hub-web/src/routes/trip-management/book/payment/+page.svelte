<script lang="ts" context="module">
  function getDefaultPassengers(passengers: PassengerPickerData): PartialPassengerData[] {
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
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import Payment from "./payment.svelte";
  import Fees from "./fees.svelte";

  import PassengerEntry, {
    getPassengerValidator,
    type PartialPassengerData,
  } from "./passenger-entry.svelte";
  import ContactInformation, {
    type PartialContactDetailsModel,
  } from "./contact-information.svelte";
  import Countdown from "../countdown.svelte";
  import { z } from "zod";
  import { pendableCall } from "utils/pendable-call";
  import { sleep } from "utils/common";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import {
    contactDetailsModel,
    type CreateOrderMarkupsModel,
  } from "integration/junction-mobile-api/schemas/order";
  import PriceDialog from "components/ui/dialogues/price-dialog.svelte";
  import Summary from "../../components/summary/summary.svelte";
  import tripManagement from "../../../integration/trip-management/trip-management";
  import type { PassengerPickerData } from "../../components/trip-search/passenger-picker/passenger-picker.svelte";
  import { onDestroy } from "svelte";

  export let data;

  let payment: Payment | undefined;
  let bookingData: {
    passengers: PartialPassengerData[];
    contactDetails: PartialContactDetailsModel;
  } = {
    passengers: getDefaultPassengers(data.searchData.passengers),
    contactDetails: { phone: {}, address: { street: {} } },
  };
  let errors: z.ZodFormattedError<z.infer<typeof bookingDetailsValidator>> | undefined = undefined;
  let { priceQuote, paymentIntent } = data;
  let pollSignal = { cancelled: false };
  let orderMarkups: CreateOrderMarkupsModel;

  $: bookingDetailsValidator = z.object({
    passengers: z.array(getPassengerValidator(priceQuote.required)),
    contactDetails: contactDetailsModel.model,
  });
  $: if (browser && !paymentIntent) {
    updatePaymentIntentAndPriceQuote();
  }
  $: shouldCreateOrderMarkups =
    orderMarkups?.serviceFee?.amount > 0 && orderMarkups?.agencyMarkup?.amount > 0;

  async function updatePaymentIntentAndPriceQuote(): Promise<void> {
    const nextPriceQuote = await tripManagement.getPriceQuote();

    if (!nextPriceQuote.price && !pollSignal.cancelled) {
      await sleep(2000);

      return updatePaymentIntentAndPriceQuote();
    }

    const nextPaymentIntent = await tripManagement.getPaymentIntent();

    [priceQuote, paymentIntent] = [nextPriceQuote, nextPaymentIntent];
  }

  function cancel(): void {
    goto(routeConfig.routes.tripManagement.routes.book.routes.select.root);
  }

  async function createOrder(): Promise<boolean> {
    if (data.orderId) {
      return true;
    }

    if (!paymentIntent) {
      return false;
    }

    errors = undefined;
    const validationResult = bookingDetailsValidator.safeParse(bookingData);

    if (!validationResult.success) {
      errors = validationResult.error.format();

      return false;
    }

    try {
      const result = await tripManagement.createOrder({
        priceQuoteId: priceQuote.id,
        passengers: validationResult.data.passengers,
        contactDetails: validationResult.data.contactDetails,
        paymentId: paymentIntent.id,
      });

      if (result.success) {
        data.orderId = result.order.id;
        return true;
      }

      errors = result.errors;

      return false;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }

      return false;
    }
  }

  async function createOrderMarkups(): Promise<boolean> {
    if (!data.orderId) {
      return false;
    }

    orderMarkups.orderId = data.orderId;

    // TODO: implement validation

    try {
      const result = await tripManagement.createOrderMarkups({ ...orderMarkups });

      if (result.success) {
        return true;
      }

      errors = result.errors;

      return false;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }

      return false;
    }
  }

  const { pending, func: pay } = pendableCall(async () => {
    if (!payment) {
      return;
    }

    if (!(await payment.pay())) {
      return;
    }

    if (!(await createOrder())) {
      return;
    }

    if (shouldCreateOrderMarkups) {
      if (!(await createOrderMarkups())) {
        return;
      }
    }

    await goto(routeConfig.routes.tripManagement.routes.book.routes.confirmation.root);
  });

  onDestroy(() => (pollSignal.cancelled = true));
</script>

<svelte:head>
  <title>Payment · Book · Trip Management · Junction Hub</title>
</svelte:head>

{#if data.selected.originalPrice && priceQuote.price}
  <PriceDialog
    originalPrice={data.selected.originalPrice}
    newPrice={priceQuote.price}
    on:cancel={cancel}
  />
{/if}

<div class="content">
  <Countdown expiresAt={priceQuote.expiresAt} show />

  <div class="wrapper">
    <div class="column passengers">
      {#each bookingData.passengers as passenger, idx}
        <PassengerEntry
          bind:passenger
          errors={errors?.passengers?.[idx]}
          required={priceQuote.required}
          passengerNumber={idx + 1}
        />
      {/each}
    </div>

    <div class="column payment">
      <Summary {priceQuote} passengers={data.searchData.passengers} />
      <Fees {priceQuote} bind:orderMarkups />
      <Payment bind:this={payment} bind:paymentIntent />
      <ContactInformation
        countries={data.countries}
        bind:contactDetails={bookingData.contactDetails}
        errors={errors?.contactDetails}
      />
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button
      size="small"
      variant="text"
      href={routeConfig.routes.tripManagement.routes.book.routes.select.root}
    >
      Previous
    </Button>
    <Button size="small" on:click={pay} disabled={!paymentIntent}>
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
