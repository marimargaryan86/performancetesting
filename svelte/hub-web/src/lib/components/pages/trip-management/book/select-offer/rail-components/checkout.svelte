<script lang="ts">
  import type { TripType } from "../../search/trip-search-data";
  import type { PartialSelectedOfferData } from "$lib/booking-manager/booking-manager";
  import { createEventDispatcher } from "svelte";
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "$lib/i18n";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { writable, type Writable } from "svelte/store";
  import TripSummary from "./trip-summary.svelte";
  import type { TripDirection } from "$lib/models/trip";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { getOffer } from "$lib/utils/offer";

  const t = getTranslator();
  const locale = getLocale();
  const dispatch = createEventDispatcher<{
    createpricequote: Writable<boolean>;
    changedirection: TripDirection;
  }>();

  export let offers: MobileSchemas.Offer[];
  export let tripType: TripType;
  export let selected: PartialSelectedOfferData;
  export let tripDirection: TripDirection;

  const pending = writable(false);

  $: outbound = selected.outbound;
  $: inbound = selected.inbound;
  $: offer = getOffer({ offers, tripType, outbound, inbound });
  $: totalPrice = outbound
    ? {
        amount: outbound.price.total.amount + (inbound?.price.total.amount ?? 0),
        currency: outbound.price.total.currency,
      }
    : undefined;
  $: proceedDisabled = !offer || !outbound || (tripType === "round-trip" && !inbound);

  function createPriceQuote(): void {
    dispatch("createpricequote", pending);
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
