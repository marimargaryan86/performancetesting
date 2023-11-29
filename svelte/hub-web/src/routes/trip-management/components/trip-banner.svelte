<script lang="ts">
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import type { OfferSegmentLeg } from "integration/common/schemas/offer-segment-leg";
  import { tripStore } from "../../../stores/tripStore";
  import { slideFade } from "transitions/slide-fade";
  import { getLegsFromPriceQuote } from "utils/offer";
  import { formatDateStringFromDate } from "utils/date-time";

  export let priceQuote: TripOfferPriceQuote;
  let legs: OfferSegmentLeg[] = [];
  let departureLeg: OfferSegmentLeg | undefined;
  let arrivalLeg: OfferSegmentLeg | undefined;
  let departureDateTime = "";
  let arrivalDateTime = "";

  // Reactive assignments for legs and related data
  $: {
    legs = getLegsFromPriceQuote(priceQuote);
    departureLeg = legs.length > 0 ? legs[0] : undefined;
    arrivalLeg = legs.length > 0 ? legs[legs.length - 1] : undefined;
    departureDateTime = departureLeg
      ? formatDateStringFromDate(departureLeg.departureAt, departureLeg.origin.timeZone)
      : "";
    arrivalDateTime = arrivalLeg
      ? formatDateStringFromDate(arrivalLeg.arrivalAt, arrivalLeg.destination.timeZone)
      : "";

    // Update trip store
    tripStore.update((store) => ({
      ...store,
      legs,
      departureLeg,
      arrivalLeg,
      departureDateTime,
      arrivalDateTime,
      departureStationName: departureLeg?.origin.name,
      arrivalStationName: arrivalLeg?.destination.name,
    }));
  }
</script>

<div transition:slideFade={{ duration: 300 }}>
  <div class="content">
    <p class="typography title-medium">{departureDateTime}</p>
    {#each legs as leg}
      <p class="typography title-medium">{leg.origin.name} {"→"} {leg.destination.name}</p>
    {/each}
    <p class="typography title-medium">{$tripStore.passengersPresentation}</p>
  </div>
</div>

<style>
  .content {
    display: flex;
    flex-wrap: nowrap;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    max-width: 100%;
    padding: 16px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    background-color: var(--color-main-primary-50);
    border: 1px solid transparent;
    border-radius: 16px;
    transition:
      border-color 200ms ease,
      background-color 200ms ease;
  }

  .content > :global(*) {
    flex-shrink: 0;
    font-size: 16px;
  }
</style>
