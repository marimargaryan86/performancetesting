<script lang="ts">
  import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import { formatAmount } from "$lib/formatting/currency";
  import { slideFade } from "~/transitions/slide-fade";
  import { getTotalPriceBreakdown } from "~/utils/offer";
  import Collapsible from "../collapsible.svelte";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import SummaryItinerary from "./summary-itinerary.svelte";
  import {
    getPassengersPresentation,
    type PassengerPickerData,
  } from "../trip-search/passenger-picker/passenger-picker.svelte";
  import { createEventDispatcher } from "svelte";
  import { getLocale, getTranslator } from "~/i18n";

  export let priceQuote: TripOfferPriceQuote | undefined = undefined;
  export let passengers: PassengerPickerData;

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

<Collapsible bind:this={collapsible} title={$t("words.summary")}>
  <div class="details">
    {#if priceQuote}
      <p typography="label-large">
        {$t("words.passenger_other")}
        <span weight="bold">{getPassengersPresentation(passengers, $t)}</span>
      </p>

      <p typography="label-large">
        {$t("words.fareBrand", { count: priceQuote.options.length })}

        <span weight="bold">
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
</style>
