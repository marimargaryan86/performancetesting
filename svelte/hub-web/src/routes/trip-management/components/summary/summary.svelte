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
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { slideFade } from "transitions/slide-fade";
  import { getTotalPriceBreakdown } from "utils/offer";

  export let priceQuote: TripOfferPriceQuoteModel | undefined = undefined;
  export let passengers: PassengerCountData;

  $: priceBreakdown = priceQuote ? getTotalPriceBreakdown(priceQuote) : undefined;
  $: totalPrice = priceQuote?.price;
  $: expanded = Boolean(totalPrice && priceBreakdown);

  function toggle(): void {
    expanded = !expanded;
  }
</script>

<div class="summary">
  <button class="summary-title" on:click={toggle}>
    <span class="typography title-medium bold">Summary</span>
    <ChevronIcon size="20px" direction={expanded ? "up" : "down"} />
  </button>

  {#if totalPrice}
    {#if expanded}
      <div class="details" transition:slideFade={{ duration: 300 }}>
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
    {/if}

    <div class="price">
      {#if expanded}
        <div transition:slideFade={{ duration: 300 }} class="price-breakdown">
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
          {formatAmount(totalPrice, undefined, true)}
        </em>
      </div>
    </div>
  {/if}
</div>

<style>
  .summary {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 24px 40px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .summary-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0;
    color: var(--color-main-primary-900);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

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
