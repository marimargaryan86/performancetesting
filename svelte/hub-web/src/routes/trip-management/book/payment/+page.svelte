<script lang="ts" context="module">
  function getDefaultPassengers(passengers: PassengerPickerData): PartialPassengerData[] {
    return (Object.keys(passengers) as unknown as (keyof PassengerPickerData)[]).flatMap((type) =>
      Array(passengers[type])
        .fill(undefined)
        .map<PartialPassengerData>(() => ({ type })),
    );
  }
</script>

<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import Payment from "./payment.svelte";
  import Fees from "./fees.svelte";
  import PassengerEntry, { type PartialPassengerData } from "./passenger-entry.svelte";
  import ContactInformation, { contactDetailsModel } from "./contact-information.svelte";
  import Countdown from "../countdown.svelte";
  import { z } from "zod";
  import { sleep } from "utils/common";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
  import PriceDialog from "components/ui/dialogues/price-dialog.svelte";
  import Summary from "../../components/summary/summary.svelte";
  import tripManagement from "../../../integration/trip-management/trip-management";
  import type { PassengerPickerData } from "../../components/trip-search/passenger-picker/passenger-picker.svelte";
  import { onDestroy } from "svelte";
  import type { ContactDetails } from "integration/junction-mobile-api/schemas/journey";
  import FareRulesDialog from "../../components/fare-rules-dialog.svelte";
  import { getPassengerValidator } from "utils/passenger";
  import { writable } from "svelte/store";
  import { formatAmount } from "formatting/currency";
  import TripBanner from "../../components/trip-banner.svelte";

  export let data;

  let fareRulesDialog: FareRulesDialog | undefined;
  let payment: Payment | undefined;
  let bookingData: {
    passengers: PartialPassengerData[];
    contact: ContactDetails;
  } = {
    passengers: getDefaultPassengers(data.searchData.passengers),
    contact: {
      phone: data.profile.contacts[0]?.phone ?? "",
      address: {
        street: {
          line1: data.profile.company.address.street?.line1 ?? "",
          line2: data.profile.company.address.street?.line2,
        },
        city: data.profile.company.address.city ?? "",
        countryCode: data.profile.company.address.countryCode ?? "",
        postalCode: data.profile.company.address.postalCode ?? "",
      },
      email: data.profile.contacts[0]?.email ?? "",
    },
  };
  let errors: z.ZodFormattedError<z.infer<typeof bookingDetailsValidator>> | undefined = undefined;
  let { priceQuote, paymentIntent } = data;
  let pollSignal = { cancelled: false };
  let orderMarkups: MarkupsCreate;

  const pending = writable(false);

  $: bookingDetailsValidator = z.object({
    passengers: z.array(getPassengerValidator(priceQuote.required)),
    contact: contactDetailsModel,
  });
  $: if (browser && !paymentIntent) {
    updatePaymentIntentAndPriceQuote();
  }
  $: shouldCreateOrderMarkups =
    orderMarkups?.serviceFee?.amount > 0 && orderMarkups?.agencyMarkup?.amount > 0;

  async function updatePaymentIntentAndPriceQuote(): Promise<void> {
    const nextPriceQuote = await tripManagement.getPriceQuote();

    if (!nextPriceQuote.price.total && !pollSignal.cancelled) {
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
        contact: validationResult.data.contact,
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

  async function pay(): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;

      if (!payment) {
        return;
      }

      if (!(await payment.pay())) {
        return;
      }

      if (!(await createOrder())) {
        return;
      }

      if (shouldCreateOrderMarkups && !(await createOrderMarkups())) {
        return;
      }

      await goto(routeConfig.routes.tripManagement.routes.book.routes.confirmation.root);
    } finally {
      $pending = false;
    }
  }

  onDestroy(() => (pollSignal.cancelled = true));
</script>

<svelte:head>
  <title>Payment · Book · Trip Management · Junction Hub</title>
</svelte:head>

{#if data.selected.originalPrice && priceQuote.price.total}
  <PriceDialog
    originalPrice={data.selected.originalPrice}
    newPrice={priceQuote.price.total}
    on:cancel={cancel}
  />
{/if}

<FareRulesDialog bind:this={fareRulesDialog} {priceQuote} />

<div class="content">
  <TripBanner {priceQuote} passengers={data.searchData.passengers} />

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
      <Summary
        {priceQuote}
        on:showFareRules={fareRulesDialog?.open}
        passengers={data.searchData.passengers}
      />
      <Fees {priceQuote} bind:orderMarkups />
      <Payment bind:this={payment} bind:paymentIntent />
      <ContactInformation bind:data={bookingData.contact} errors={errors?.contact} />
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button
      size="small"
      variant="outline"
      href={routeConfig.routes.tripManagement.routes.book.routes.select.root}
    >
      Previous
    </Button>

    <div class="total">
      <div>
        <span class="typography body-large bold">Total to pay</span>
      </div>
      <em class="typography body-large bold">
        {#if priceQuote?.price.total}
          {formatAmount(priceQuote?.price.total, true)}
        {:else}
          <LoadingIcon size="14px" />
        {/if}
      </em>
    </div>

    <Button size="small" on:click={pay} disabled={!paymentIntent}>
      Book

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

  .content > :global(.countdown),
  .content > :global(.trip-banner) {
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
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 1104px;
  }

  .total {
    display: flex;
    gap: 8px;
    margin-left: auto;
    padding: 8px;
    background-color: var(--color-main-primary-50);
    border-radius: 8px;
  }

  .total > em {
    color: var(--color-main-primary-500);
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
