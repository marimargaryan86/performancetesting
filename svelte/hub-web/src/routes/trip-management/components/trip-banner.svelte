<script lang="ts">
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import { slideFade } from "transitions/slide-fade";
  import { getLegsFromPriceQuote } from "utils/offer";
  import {
    getPassengersPresentation,
    type PassengerPickerData,
  } from "./trip-search/passenger-picker/passenger-picker.svelte";

  export let priceQuote: TripOfferPriceQuote;
  export let passengers: PassengerPickerData;

  $: legs = getLegsFromPriceQuote(priceQuote);
  $: departureLeg = legs[0];
  $: arrivalLeg = legs[legs.length - 1];
</script>

<div transition:slideFade={{ duration: 300 }} class="trip-banner typography body-large">
  {#if departureLeg && arrivalLeg}
    <p>
      {departureLeg.departureAt.toLocaleDateString("en-GB", {
        month: "long",
        day: "numeric",
        year: "numeric",
        timeZone: departureLeg.origin.timeZone,
      })}
    </p>

    <p>
      {departureLeg.origin.name}
      {"→"}
      {arrivalLeg.destination.name}
    </p>

    <p class="truncate">
      {getPassengersPresentation(passengers)}
    </p>
  {:else}
    <p>Loading trip details...</p>
  {/if}
</div>

<style>
  .trip-banner {
    display: flex;
    flex-wrap: nowrap;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    background-color: var(--color-main-primary-50);
    border: 1px solid transparent;
    border-radius: 16px;
  }

  .trip-banner > p {
    flex-shrink: 0;
  }

  .truncate {
    width: 25%;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
</style>
