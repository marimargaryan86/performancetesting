<script lang="ts">
  import type { TripType } from "../../search/trip-search-data";
  import type { PartialSelectedOffer } from "$lib/booking-manager/booking-manager";
  import { createEventDispatcher } from "svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "$lib/i18n";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { writable, type Writable } from "svelte/store";
  import TripSummary from "./trip-summary.svelte";
  import type { TripDirection } from "$lib/models/trip";

  const t = getTranslator();
  const locale = getLocale();
  const dispatch = createEventDispatcher<{
    createpricequote: {
      offer: MobileSchemas.Offer;
      outbound: MobileSchemas.OfferOption;
      inbound?: MobileSchemas.OfferOption;
      pending: Writable<boolean>;
    };
    changedirection: TripDirection;
  }>();

  export let tripType: TripType;
  export let offers: MobileSchemas.Offer[];
  export let selected: PartialSelectedOffer;
  export let tripDirection: TripDirection;

  const pending = writable(false);

  $: offer = offers.find((item) => item.id === selected.offerId);
  $: outbound = offers
    .flatMap((item) => item.groups.flatMap((group) => group.options))
    .find((option) => option.id === selected.optionIds?.[0]);
  $: inbound = offer?.groups
    .flatMap((group) => group.options)
    .find((option) => option.id === selected.optionIds?.[1]);
  $: totalPrice = outbound
    ? {
        amount: outbound.price.total.amount + (inbound?.price.total.amount ?? 0),
        currency: outbound.price.total.currency,
      }
    : undefined;
  $: proceedDisabled = !offer || !outbound || (tripType === "round-trip" && !inbound);

  function createPriceQuote(): void {
    if (!(offer && outbound)) {
      return;
    }

    if (tripType === "round-trip" && !inbound) {
      return;
    }

    dispatch("createpricequote", {
      offer,
      outbound,
      inbound,
      pending,
    });
  }

  function changeDirection(direction: TripDirection): void {
    dispatch("changedirection", direction);
  }
</script>

<div class="checkout">
  {#if tripType === "round-trip" || outbound}
    <TripSummary
      focused={tripDirection === "outbound"}
      class="outbound"
      title={$t("words.outbound")}
      direction="right"
      start={outbound?.detailsList[0]?.details?.legs[0]}
      end={outbound?.detailsList.at(-1)?.details?.legs.at(-1)}
      showTripDirection={tripType === "round-trip"}
    >
      <button
        on:click={changeDirection.bind(changeDirection, "outbound")}
        slot="action"
        class="change"
        typography="body-medium"
      >
        {$t("actions.change")}
      </button>
    </TripSummary>
  {/if}

  {#if tripType === "round-trip"}
    <TripSummary
      focused={tripDirection === "inbound"}
      class="inbound"
      title={$t("words.inbound")}
      direction="left"
      start={inbound?.detailsList[0]?.details?.legs[0]}
      end={inbound?.detailsList.at(-1)?.details?.legs.at(-1)}
    >
      <button
        on:click={changeDirection.bind(changeDirection, "inbound")}
        slot="action"
        class="change"
        typography="body-medium"
      >
        {$t("actions.change")}
      </button>
    </TripSummary>
  {/if}

  {#if totalPrice}
    <div class="price">
      <strong typography="title-large" weight="bold">
        {formatAmount(totalPrice, $locale, { sign: true })}
      </strong>
      <span typography="label-medium">{$t("sentences.totalAmount")}</span>
    </div>
  {/if}

  <button
    variant="primary"
    size="medium"
    on:click={createPriceQuote}
    class="proceed"
    disabled={proceedDisabled}
  >
    {$t("actions.next")}

    {#if $pending}
      <LoadingIcon />
    {/if}
  </button>
</div>

<style>
  .checkout {
    display: grid;
    grid-template-columns: 1fr 1fr max-content max-content;
    gap: 16px;
    align-items: center;
    width: 100%;
    margin: -4px 0;
    color: var(--color-common-light-strong);
  }

  .checkout > :global(.outbound) {
    grid-column: 1;
  }

  .checkout > :global(.inbound) {
    grid-column: 2;
  }

  .price {
    display: flex;
    flex-flow: column;
    grid-column: 3;
    gap: 2px;
    align-items: flex-end;
  }

  .price > span {
    color: var(--color-common-light-soft);
  }

  button.proceed {
    grid-column: 4;
    width: 140px;
  }

  button.change {
    padding: 0;
    color: var(--color-common-light-medium);
    text-decoration: underline;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
