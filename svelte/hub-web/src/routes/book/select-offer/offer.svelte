<script lang="ts" context="module">
  export type OfferModel = {
    id: number;
    operator: string;
    stops: string;
    type: string;
    departureTime: string;
    arrivalTime: string;
    journeyDuration: string;
    departureStation: string;
    arrivalStation: string;
    departureStationInfo: string;
    arrivalStationInfo: string;
    price: string;
    selected: boolean;
    alternativeFares: {
      id: number;
      title: string;
      type: string;
      description: string;
      price: string;
      selected: boolean;
    }[];
  };
</script>

<script lang="ts">
  import Button from "components/ui/button.svelte";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import Arrow from "components/icons/arrow-icon.svelte";
  import AlternativeFares from "./alternative-fares-slider/slider.svelte";
  import { fly } from "svelte/transition";
  import { createEventDispatcher } from "svelte";

  export let offer: OfferModel;

  const dispatch = createEventDispatcher<{
    toggleSelectedOffer: { id: number };
    fareSelected: unknown;
  }>();

  function toggleSelectedOffer(): void {
    dispatch("toggleSelectedOffer", {
      id: offer.id,
    });
  }

  function handleKeyToggleSelectedOffer(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      toggleSelectedOffer();
    }
  }
</script>

<div class="offer" class:selected={offer.selected}>
  <div class="offer-preview typography body-small">
    <img src="/images/renfe-logo.png" width="26" height="26" alt="logo" />
    <span>{offer.operator} • {offer.stops} • {offer.type}</span>
  </div>
  <div class="offer-info typography body-medium-weight-600">
    <div class="offer-direction">
      <div class="circle" />
      <div class="line" />
      <div class="circle" />
    </div>
    <div class="offer-time">
      <div class="departure-time">{offer.departureTime}</div>
      <div class="journey-duration grey-color typography body-small">{offer.journeyDuration}</div>
      <div class="arrival-time">{offer.arrivalTime}</div>
    </div>
    <div class="offer-stations">
      <div class="departure-station station">
        <span>{offer.departureStation}</span>
        <span class="grey-color station-info typography body-small"
          >{offer.departureStationInfo}</span
        >
      </div>
      <div class="arrival-station station">
        <span>{offer.arrivalStation}</span>
        <span class="grey-color station-info typography body-small">{offer.arrivalStationInfo}</span
        >
      </div>
    </div>
    <div class="offer-price">
      <div class="price-border" />
      <div class="price-info">
        <div class="from-price typography body-small">
          From <span class="price">{offer.price}</span>
        </div>
        {#if !offer.selected}
          <div transition:fly|local={{ duration: 200, x: 100 }}>
            <Button variant="outline" size="xl-small" on:click={toggleSelectedOffer}>
              <span class="typography body-small-weight-600">Details</span>
              <Arrow color="var(--color-main-primary-500)" />
            </Button>
          </div>
        {/if}
      </div>
    </div>
  </div>
  <div
    on:click={toggleSelectedOffer}
    on:keyup={handleKeyToggleSelectedOffer}
    class="alternative-fares-toggle"
  >
    <span>Alternative fares</span>
    <ChevronIcon direction={offer.selected ? "up" : "down"} color="var(--color-main-primary-500)" />
  </div>
  {#if offer.selected}
    <div class="expanded" transition:fly|local={{ duration: 200, x: 100 }}>
      <AlternativeFares
        on:fareSelected
        alternativeFares={offer.alternativeFares}
        offerId={offer.id}
      />
    </div>
  {/if}
</div>

<style>
  .offer {
    margin-bottom: 16px;
    padding: 8px 24px 24px;
    background-color: var(--color-common-dark-strong);
    border-top: 16px solid var(--color-common-dark-strong);
    border-right: 2px solid var(--color-common-dark-strong);
    border-bottom: 2px solid var(--color-common-dark-strong);
    border-left: 2px solid var(--color-common-dark-strong);
    border-radius: 16px;
    transition: border-color 0.2s ease-in-out;
  }

  .offer-info {
    display: flex;
  }

  .offer-preview {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 24px;
  }

  .offer-direction {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
    width: 16px;
  }

  .offer-time {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-left: 12px;
  }

  .offer-stations {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-left: 17px;
  }

  .offer-price {
    display: flex;
    justify-content: space-between;
    margin-left: auto;
  }

  .price-info {
    display: flex;
    flex-direction: column;
    gap: 16px;
    align-items: flex-end;
  }

  .price-info .from-price {
    display: flex;
    gap: 4px;
    align-items: center;
    color: var(--color-common-light-strong);
  }

  .price {
    font-weight: 600;
    font-size: 22px;
    line-height: 26px;
  }

  .price-border {
    margin-right: 40px;
    border-left: 1px solid #d9d9d9;
  }

  .station {
    position: relative;
    display: flex;
    flex-direction: column;
  }

  .station-info {
    position: absolute;
    top: 24px;
  }

  .grey-color {
    color: var(--color-main-neutral-500);
  }

  .circle {
    width: 16px;
    height: 16px;
    border: 1px solid #000000;
    border-radius: 50%;
  }

  .line {
    height: 40px;
    border-left: 1px solid var(--color-main-neutral-500);
  }

  .alternative-fares-toggle {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
    margin-top: 26px;
    color: var(--color-main-primary-500);
    cursor: pointer;
  }

  .selected {
    border-top: 16px solid var(--color-main-primary-600);
    border-right: 2px solid var(--color-main-primary-600);
    border-bottom: 2px solid var(--color-main-primary-600);
    border-left: 2px solid var(--color-main-primary-600);
    transition: border-color 0.2s ease-in-out;
  }
</style>
