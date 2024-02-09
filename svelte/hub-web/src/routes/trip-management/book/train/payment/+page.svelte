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
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import routeConfig from "~/route-config";
  import Payment from "./payment.svelte";
  import Fees from "./fees.svelte";
  import PassengerEntry, { type PartialPassengerData } from "./passenger-entry.svelte";
  import ContactInformation, { contactDetailsModel } from "./contact-information.svelte";
  import Countdown from "../countdown.svelte";
  import { z } from "zod";
  import { goto } from "$app/navigation";
  import PriceDialog from "~/components/ui/dialogues/price-dialog.svelte";
  import Summary from "../../../components/summary/summary.svelte";
  import type { PassengerPickerData } from "../../../components/trip-search/passenger-picker/passenger-picker.svelte";
  import { onDestroy } from "svelte";
  import type { ContactDetails } from "~/integration/junction-mobile-api/schemas/journey";
  import FareRulesDialog from "../../../components/fare-rules-dialog.svelte";
  import { getPassengerValidator } from "~/utils/passenger";
  import { writable } from "svelte/store";
  import { formatAmount } from "$lib/formatting/currency";
  import TripBanner from "../../../components/trip-banner.svelte";
  import { getPageTitle } from "~/utils/page-title";
  import { getLocale, getTranslator } from "~/i18n";
  import type { TripOfferPriceQuoteCompleted } from "~/integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import { manager, markupsModel, type Markups, type PartialMarkups } from "../../../booking-flow";
  import { browser } from "$app/environment";

  export let data;

  let fareRulesDialog: FareRulesDialog | undefined;
  let payment: Payment | undefined;
  let bookingData: {
    passengers: PartialPassengerData[];
    contact: ContactDetails;
  } = {
    passengers: getDefaultPassengers(data.bookingSession.searchData.passengers),
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
  let priceQuote: TripOfferPriceQuoteCompleted | undefined;

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

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.book.title"),
      $t("pages.tripManagement.pages.book.pages.payment.title"),
    )}
  </title>
</svelte:head>

{#if priceQuote}
  <PriceDialog
    originalPrice={data.bookingSession.selectedOffer.originalPrice}
    newPrice={priceQuote.price.total}
    on:cancel={cancel}
  />

  <FareRulesDialog bind:this={fareRulesDialog} {priceQuote} />
{/if}

<div class="content">
  {#if priceQuote}
    <TripBanner {priceQuote} passengers={data.bookingSession.searchData.passengers} />
  {/if}

  <Countdown expiresAt={data.bookingSession.priceQuote.expiresAt} show />

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

<div class="actions">
  <div class="wrapper">
    <a
      variant="outline"
      size="small"
      href={routeConfig.routes.tripManagement.routes.book.routes.train.routes.select.root}
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

    <button variant="primary" size="small" on:click={book} disabled={!data.bookingSession.payment}>
      {$t("actions.book")}

      {#if $pending}
        <LoadingIcon />
      {/if}
    </button>
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

  .actions > .wrapper > button,
  .actions > .wrapper > a {
    width: 140px;
  }
</style>
