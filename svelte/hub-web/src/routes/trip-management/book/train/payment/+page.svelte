<script lang="ts">
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import routeConfig from "$lib/route-config";
  import Payment from "$lib/components/pages/trip-management/booking-flow-train/payment/payment.svelte";
  import Fees from "$lib/components/pages/trip-management/booking-flow-train/payment/fees.svelte";
  import PassengerEntry from "$lib/components/pages/trip-management/booking-flow-train/payment/passenger-entry.svelte";
  import type { PartialPassengerData } from "$lib/models/passenger";
  import ContactInformation from "$lib/components/pages/trip-management/booking-flow-train/payment/contact-information.svelte";
  import { contactDetailsModel } from "$lib/models/contact-details";
  import Countdown from "$lib/components/pages/trip-management/booking-flow-train/countdown.svelte";
  import { z } from "zod";
  import { goto } from "$app/navigation";
  import PriceDialog from "$lib/components/ui/dialogues/price-dialog.svelte";
  import Summary from "$lib/components/pages/trip-management/booking-flow-train/summary/summary.svelte";
  import { onDestroy } from "svelte";
  import FareRulesDialog from "$lib/components/pages/trip-management/booking-flow-train/fare-rules-dialog.svelte";
  import { getDefaultPassengers, getPassengerValidator } from "$lib/utils/passenger";
  import { writable } from "svelte/store";
  import { formatAmount } from "$lib/formatting/currency";
  import TripBanner from "$lib/components/pages/trip-management/booking-flow-train/trip-banner.svelte";
  import { getLocale, getTranslator } from "$lib/i18n";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import {
    manager,
    markupsModel,
    type Markups,
    type PartialMarkups,
  } from "$lib/booking-manager/booking-manager";
  import { browser } from "$app/environment";
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import { passengerParser } from "$lib/components/pages/trip-management/booking-flow-train/trip-search-data.js";

  export let data;

  let fareRulesDialog: FareRulesDialog | undefined;
  let payment: Payment | undefined;
  let bookingData: {
    passengers: PartialPassengerData[];
    contact: MobileSchemas.ContactDetails;
  } = {
    passengers: getDefaultPassengers(
      passengerParser.fromSearchData(data.bookingSession.searchData.passengers),
    ),
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
  let errors:
    | z.ZodFormattedError<z.infer<typeof bookingDetailsValidator> & { markups: Markups }>
    | undefined = undefined;
  let markups: PartialMarkups = data.bookingSession.markups ?? {};
  let priceQuotePollController: AbortController | undefined;
  let priceQuote: MobileSchemas.TripOfferPriceQuoteCompleted | undefined;

  $: priceQuoteId = data.bookingSession.priceQuote.id;
  $: updatePriceQuote(priceQuoteId);

  const locale = getLocale();
  const t = getTranslator();
  const pending = writable(false);

  $: bookingDetailsValidator = z.object({
    passengers: z.array(getPassengerValidator(priceQuote?.required ?? [])),
    contact: contactDetailsModel,
  });

  async function updatePriceQuote(nextPriceQuoteId: string): Promise<void> {
    if (!browser) {
      return;
    }

    priceQuotePollController?.abort();
    priceQuotePollController = new AbortController();
    priceQuote = await manager.getPriceQuote(
      data.bookingSession,
      nextPriceQuoteId,
      priceQuotePollController.signal,
    );

    if (!data.bookingSession.payment) {
      data.bookingSession.payment = await manager.getPayment(data.bookingSession, priceQuote);
    }
  }

  function cancel(): void {
    goto(routeConfig.routes.tripManagement.routes.book.routes.train.routes.select.root);
  }

  async function createOrder(): Promise<boolean> {
    if (data.bookingSession.order) {
      return true;
    }

    if (!(data.bookingSession.payment && priceQuote)) {
      return false;
    }

    try {
      data.bookingSession.order = await manager.createOrder(data.bookingSession, {
        ...bookingDetailsValidator.parse(bookingData),
        payment: data.bookingSession.payment,
        priceQuote,
      });

      return true;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }

      return false;
    }
  }

  async function createMarkups(): Promise<boolean> {
    if (!(data.bookingSession.order && data.bookingSession.payment)) {
      return false;
    }

    try {
      const parsed = markupsModel.parse(markups);

      if (parsed.agencyMarkup.amount === 0 && parsed.serviceFee.amount === 0) {
        return true;
      }

      markups = await manager.createMarkups(data.bookingSession, data.bookingSession.order, parsed);

      return true;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = { _errors: [], markups: err.format() };
      }

      return false;
    }
  }

  async function book(): Promise<void> {
    if ($pending || !data.bookingSession.payment || !payment) {
      return;
    }

    try {
      $pending = true;

      if (!data.bookingSession.payment.confirmed) {
        if (!(await payment.pay())) {
          return;
        }

        data.bookingSession.payment = manager.confirmPayment(
          data.bookingSession,
          data.bookingSession.payment,
        );
      }

      if (!(await createOrder())) {
        return;
      }

      if (!(await createMarkups())) {
        return;
      }

      await goto(
        routeConfig.routes.tripManagement.routes.book.routes.train.routes.confirmation.root,
      );
    } finally {
      $pending = false;
    }
  }

  onDestroy(() => {
    if (browser) {
      priceQuotePollController?.abort();
    }
  });
</script>

{#if priceQuote}
  <PriceDialog
    originalPrice={data.bookingSession.selectedOffer.originalPrice}
    newPrice={priceQuote.price.total}
    on:cancel={cancel}
  />

  <FareRulesDialog bind:this={fareRulesDialog} {priceQuote} />
{/if}

<BookingLayout
  showActions
  pageTitle={$t("pages.tripManagement.pages.book.pages.payment.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.payment.subTitle")}
>
  <div class="content">
    {#if priceQuote}
      <TripBanner {priceQuote} passengers={data.bookingSession.searchData.passengers} />
    {/if}

    <Countdown expiresAt={data.bookingSession.priceQuote.expiresAt} type="price-quote" show />

    <div class="wrapper">
      <div class="column passengers">
        {#each bookingData.passengers as passenger, idx}
          <PassengerEntry
            bind:passenger
            errors={errors?.passengers?.[idx]}
            required={priceQuote?.required ?? []}
            passengerNumber={idx + 1}
          />
        {/each}
      </div>

      <div class="column payment">
        <Summary
          {priceQuote}
          on:showFareRules={fareRulesDialog?.open}
          passengers={data.bookingSession.searchData.passengers}
        />
        <Fees {priceQuote} bind:markups errors={errors?.markups} />
        <Payment bind:this={payment} paymentIntent={data.bookingSession.payment} />
        <ContactInformation bind:data={bookingData.contact} errors={errors?.contact} />
      </div>
    </div>
  </div>

  <svelte:fragment slot="actions">
    <a
      variant="outline"
      size="small"
      href={routeConfig.routes.tripManagement.routes.book.routes.train.routes.select.root}
      class="action"
    >
      {$t("actions.previous")}
    </a>

    <div class="total">
      <div>
        <span typography="body-large" weight="bold">{$t("sentences.totalToPay")}</span>
      </div>
      <em typography="body-large" weight="bold">
        {#if priceQuote?.price.total}
          {formatAmount(priceQuote?.price.total, $locale, { sign: true })}
        {:else}
          <LoadingIcon size="14px" />
        {/if}
      </em>
    </div>

    <button
      variant="primary"
      size="small"
      on:click={book}
      disabled={!data.bookingSession.payment}
      class="action"
    >
      {$t("actions.book")}

      {#if $pending}
        <LoadingIcon />
      {/if}
    </button>
  </svelte:fragment>
</BookingLayout>

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

  button.action,
  a.action {
    width: 140px;
  }
</style>
