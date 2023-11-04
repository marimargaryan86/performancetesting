<script lang="ts" context="module">
  function getPassengersPresentation(passengers: PassengerPickerData): string {
    const { adults, children, infants } = passengers;

    return [
      adults ? `${adults} Adult${adults === 1 ? "" : "s"}` : undefined,
      children ? `${children} Child${children === 1 ? "" : "ren"}` : undefined,
      infants ? `${infants} Infant${infants === 1 ? "" : "s"}` : undefined,
    ]
      .filter(ensureDefined)
      .join(", ");
  }
</script>

<script lang="ts">
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import { ensureDefined } from "utils/array";
  import { formatAmount, formatPriceBreakdownType } from "formatting/currency";
  import { slideFade } from "transitions/slide-fade";
  import { getTotalPriceBreakdown } from "utils/offer";
  import Collapsible from "../collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SummaryItinerary from "./summary-itinerary.svelte";
  import type { PassengerPickerData } from "../trip-search/passenger-picker/passenger-picker.svelte";

  export let priceQuote: TripOfferPriceQuote | undefined = undefined;
  export let passengers: PassengerPickerData;

  let collapsible: Collapsible | undefined;

  function renderFareRulesDialog(): void {
    // TODO: implement
    alert("Rule dialog here.");
  }

  $: priceBreakdown = priceQuote ? getTotalPriceBreakdown(priceQuote) : undefined;
  $: totalPrice = priceQuote?.price.total;
</script>

<Collapsible bind:this={collapsible} title="Summary">
  <div class="details">
    {#if priceQuote}
      <p class="typography label-large">
        Passengers <span class="typography bold">{getPassengersPresentation(passengers)}</span>
      </p>

      <p class="typography label-large">
        Fare Brand{priceQuote.options.length === 1 ? "" : "s"}

        <span class="typography bold">
          {priceQuote.options.map((item) => item.brandName).join(", ")}
        </span>
      </p>

      <SummaryItinerary {priceQuote} on:showFareRules={renderFareRulesDialog} />
    {:else}
      <LoadingIcon size="24px" />
    {/if}
  </div>

  <div slot="content-after" let:expanded let:transitionTimeMs>
    <div class="price">
      {#if expanded}
        <div transition:slideFade={{ duration: transitionTimeMs }} class="price-breakdown">
          <span class="typography body-small">This price is for all passengers</span>

          {#if priceBreakdown}
            <ul>
              {#each priceBreakdown as item}
                <li>
                  <span class="typography label-medium">{formatPriceBreakdownType(item.type)}</span>
                  <span class="typography body-small bold">
                    {formatAmount(item.price, undefined, true)}
                  </span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}

      <div class="total">
        <span class="typography body-large bold">Total to pay</span>
        <em class="typography body-large bold">
          {#if totalPrice}
            {formatAmount(totalPrice, undefined, true)}
          {:else}
            <LoadingIcon size="16px" />
          {/if}
        </em>
      </div>
    </div>

    {#if expanded}
      <div class="fare-rules-wrapper">
        <p class="typography body-xsmall">
          Fares are not guaranteed until full payment is received and tickets are issued. See all
          the applicable <button class="typography body-xsmall" on:click={renderFareRulesDialog}
            >Fare Rules</button
          >
          and
          <button class="typography body-xsmall" on:click={renderFareRulesDialog}
            >Baggage Information</button
          >.
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
