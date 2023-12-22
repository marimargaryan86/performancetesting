<script lang="ts">
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import { formatAmount } from "formatting/currency";
  import { slideFade } from "transitions/slide-fade";
  import { getTotalPriceBreakdown } from "utils/offer";
  import Collapsible from "../collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SummaryItinerary from "./summary-itinerary.svelte";
  import {
    getPassengersPresentation,
    type PassengerPickerData,
  } from "../trip-search/passenger-picker/passenger-picker.svelte";
  import { createEventDispatcher } from "svelte";
  import { getLocale, getLocaleData } from "i18n";

  export let priceQuote: TripOfferPriceQuote | undefined = undefined;
  export let passengers: PassengerPickerData;

  let collapsible: Collapsible | undefined;

  const locale = getLocale();
  const i18n = getLocaleData();
  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }

  $: priceBreakdown = priceQuote ? getTotalPriceBreakdown(priceQuote) : undefined;
  $: totalPrice = priceQuote?.price.total;
</script>

<Collapsible bind:this={collapsible} title={$i18n.words.summary}>
  <div class="details">
    {#if priceQuote}
      <p class="typography label-large">
        {$i18n.words.passenger.plural}
        <span class="typography bold">{getPassengersPresentation(passengers, $i18n)}</span>
      </p>

      <p class="typography label-large">
        {$i18n.words.fareBrand[priceQuote.options.length === 1 ? "singular" : "plural"]}

        <span class="typography bold">
          {priceQuote.options.map((item) => item.brandName).join(", ")}
        </span>
      </p>

      <SummaryItinerary {priceQuote} on:showFareRules={showFareRules} />
    {:else}
      <LoadingIcon size="24px" />
    {/if}
  </div>

  <div slot="content-after" let:expanded let:transitionTimeMs>
    <div class="price">
      {#if expanded}
        <div transition:slideFade={{ duration: transitionTimeMs }} class="price-breakdown">
          <span class="typography body-small">{$i18n.sentences.thisPriceIsForAllPassengers}</span>

          {#if priceBreakdown}
            <ul>
              {#each priceBreakdown as item}
                <li>
                  <span class="typography label-medium">
                    {$i18n.priceBreakdownTypes[item.type]}
                  </span>
                  <span class="typography body-small bold">
                    {formatAmount(item.price, { locale: $locale, sign: true })}
                  </span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}

      <div class="total">
        <span class="typography body-large bold">{$i18n.sentences.totalToPay}</span>
        <em class="typography body-large bold">
          {#if totalPrice}
            {formatAmount(totalPrice, { locale: $locale, sign: true })}
          {:else}
            <LoadingIcon size="16px" />
          {/if}
        </em>
      </div>
    </div>

    {#if expanded}
      <div class="fare-rules-wrapper">
        <p class="typography body-xsmall">
          {#each $i18n.sentences.fareRulesInfo as item}
            {#if item.type === "text"}
              {item.value}
            {:else}
              <button class="typography body-xsmall" on:click={showFareRules}>{item.value}</button>
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
</style>
