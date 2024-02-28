<script lang="ts">
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { formatAmount } from "$lib/formatting/currency";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { getTotalPriceBreakdown } from "$lib/utils/offer";
  import Collapsible from "../../collapsible.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import SummaryItinerary from "./summary-itinerary.svelte";
  import { getPassengersPresentation } from "$lib/models/passenger";
  import { createEventDispatcher } from "svelte";
  import { getLocale, getTranslator } from "$lib/i18n";
  import { passengerParser } from "../../search/trip-search-data";
  import type { SearchData } from "$lib/booking-manager/booking-manager";

  let passengersExt: Date[];
  export { passengersExt as passengers };
  export let priceQuote: MobileSchemas.TripOfferPriceQuote | undefined = undefined;
  $: passengers = passengerParser.fromSearchData(passengersExt);

  export let searchData: SearchData;
  $: currentSearchData = searchData;

  export let isRoundTrip: boolean = false;

  let collapsible: Collapsible | undefined;

  const locale = getLocale();
  const t = getTranslator();
  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }

  $: priceBreakdown = priceQuote ? getTotalPriceBreakdown(priceQuote) : undefined;
  $: totalPrice = priceQuote?.price.total;
</script>

<Collapsible expandedOnMount={true} bind:this={collapsible} title={$t("words.summary")}>
  <div class="details">
    {#if priceQuote}
      <div typography="body-large" class="orig-dest" weight="bold">
        {currentSearchData.origin.name}
        <span typography="label-medium" weight="bold">{isRoundTrip ? "⇄" : "→"}</span>
        {currentSearchData.destination.name}
      </div>

      <div typography="label-large">
        {currentSearchData.outbound.toLocaleDateString($locale, {
          weekday: "short",
          day: "numeric",
          month: "short",
        })}

        {#if isRoundTrip && currentSearchData.inbound !== undefined}
          - {currentSearchData.inbound.toLocaleDateString($locale, {
            weekday: "short",
            day: "numeric",
            month: "short",
          })}
        {/if}
        ·
        {$t(`tripTypes.${isRoundTrip ? "round-trip" : "one-way"}`)}
        ·
        {getPassengersPresentation(passengers, $t)}
      </div>

      <SummaryItinerary {priceQuote} on:showFareRules={showFareRules} />
    {:else}
      <LoadingIcon size="24px" />
    {/if}
  </div>

  <div slot="content-after" let:expanded let:transitionTimeMs>
    <div class="price">
      {#if expanded}
        <div transition:slideFade={{ duration: transitionTimeMs }} class="price-breakdown">
          <span typography="body-small">{$t("sentences.thisPriceIsForAllPassengers")}</span>

          {#if priceBreakdown}
            <ul>
              {#each priceBreakdown as item}
                <li>
                  <span typography="label-medium">
                    {$t(`priceBreakdownTypes.${item.type}`)}
                  </span>
                  <span typography="body-small" weight="bold">
                    {formatAmount(item.price, $locale, { sign: true })}
                  </span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}

      <div class="total">
        <span typography="body-large" weight="bold">{$t("sentences.totalToPay")}</span>
        <em typography="body-large" weight="bold">
          {#if totalPrice}
            {formatAmount(totalPrice, $locale, { sign: true })}
          {:else}
            <LoadingIcon size="16px" />
          {/if}
        </em>
      </div>
    </div>

    {#if expanded}
      <div class="fare-rules-wrapper">
        <p typography="body-xsmall">
          {#each $t("sentences.fareRulesInfo", { returnObjects: true }) as item}
            {#if item.type === "text"}
              {item.value}
            {:else}
              <button typography="body-xsmall" on:click={showFareRules}>{item.value}</button>
            {/if}
          {/each}
        </p>
      </div>
    {/if}
  </div>
</Collapsible>

<style>
  .details {
    display: flex;
    flex-flow: column;
    gap: 4px;
    padding: 0 0 16px;
    border-bottom: var(--color-common-line-medium) 1px solid;
  }

  .details > :global(svg) {
    align-self: center;
  }

  .details > :global(.itinerary) {
    margin-top: 16px;
  }

  .price {
    margin: 0 -16px;
    padding: 16px;
    background-color: var(--color-main-primary-50);
    border-radius: 16px;
  }

  .price-breakdown {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .price-breakdown > ul {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 0 0 16px;
  }

  .price-breakdown > ul > li {
    display: flex;
    justify-content: space-between;
  }

  .total {
    display: flex;
    justify-content: space-between;
  }

  .total > em {
    color: var(--color-main-primary-500);
  }

  .fare-rules-wrapper {
    padding-top: 16px;
  }

  button {
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .orig-dest > span {
    color: var(--color-main-primary-500);
  }
</style>
