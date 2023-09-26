<script lang="ts" context="module">
  function getPassengersPresentation(passengers: PassengerCountData): string {
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
  import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
  import type { PassengerCountData } from "../../book/booking-manager.server";
  import { ensureDefined } from "utils/array";
  import { formatAmount, formatPriceBreakdownType } from "formatting/currency";
  import { slideFade } from "transitions/slide-fade";
  import { getTotalPriceBreakdown } from "utils/offer";
  import Collapsible from "../collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";

  export let priceQuote: TripOfferPriceQuoteModel | undefined = undefined;
  export let passengers: PassengerCountData;

  let collapsible: Collapsible | undefined;

  $: priceBreakdown = priceQuote ? getTotalPriceBreakdown(priceQuote) : undefined;
  $: totalPrice = priceQuote?.price;
  $: priceSet = Boolean(totalPrice && priceBreakdown);
  $: if (priceSet) {
    collapsible?.open();
  }
</script>

<Collapsible bind:this={collapsible} expandedOnMount={priceSet} title="Summary">
  <div class="details">
    <p class="typography label-large">
      Passengers <span class="typography bold">{getPassengersPresentation(passengers)}</span>
    </p>

    <p class="typography label-large">
      Fare Brand{priceQuote?.options.length === 1 ? "" : "s"}

      <span class="typography bold">
        {priceQuote?.options.map((item) => item.brandName).join(", ")}
      </span>
    </p>

    <button class="fare-rules typography body-small">View fare rules</button>
  </div>

  <div class="price" slot="content-after" let:expanded let:transitionTimeMs>
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
      <span class="typography body-large bold">Total paid</span>
      <em class="typography body-large bold">
        {#if totalPrice}
          {formatAmount(totalPrice, undefined, true)}
        {:else}
          <LoadingIcon size="16px" />
        {/if}
      </em>
    </div>
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

  .fare-rules {
    align-self: flex-end;
    color: var(--color-common-light-text-link);
    text-decoration: underline;
    background-color: transparent;
    border: 0;
    cursor: pointer;
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
</style>
