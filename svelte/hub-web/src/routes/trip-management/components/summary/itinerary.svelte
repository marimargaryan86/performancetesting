<script lang="ts" context="module">
  export type OrigDestLegs = {
    originLeg: OfferSegmentLegModel;
    destinationLeg: OfferSegmentLegModel;
  };

  function getLegs(priceQuote: TripOfferPriceQuoteModel): OfferSegmentLegModel[] {
    return (
      priceQuote.offer?.groups
        .flatMap((group) => group.details.flatMap((details) => details.legs))
        .filter(ensureDefined)
        .sort((a, b) => a.departureAt.getTime() - b.departureAt.getTime()) ?? []
    );
  }
</script>

<script lang="ts">
  import type {
    OfferSegmentLegModel,
    TripOfferPriceQuoteModel,
  } from "integration/junction-mobile-api/schemas/offer";
  import { formatDuration } from "formatting/date-time";
  import { getTimeDeltaS } from "utils/date-time";
  import Collapsible from "../collapsible.svelte";
  import { ensureDefined } from "utils/array";

  export let priceQuote: TripOfferPriceQuoteModel;

  $: legs = getLegs(priceQuote);
</script>

<Collapsible class="itinerary" title="Itinerary">
  <ul class="segments">
    {#each legs as leg}
      <li class="segment typography label-large bold">
        <span class="circle" />
        <strong>
          {leg.departureAt.toLocaleTimeString("sv-SE", {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: leg.origin.timeZone,
          })}
        </strong>
        <strong>{leg.origin.name}</strong>

        <span class="line" />
        <em class="typography body-small default">
          {formatDuration(getTimeDeltaS(leg.departureAt, leg.arrivalAt))}
        </em>
        <em />

        <span class="circle" />
        <strong>
          {leg.arrivalAt.toLocaleTimeString("sv-SE", {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: leg.destination.timeZone,
          })}
        </strong>
        <strong>{leg.destination.name}</strong>
      </li>
    {/each}
  </ul>

  <div class="fare-rules">
    <button class="typography body-small">View fare rules</button>
  </div>
</Collapsible>

<style>
  :global(.collapsible.itinerary) {
    --border-radius: 0;
    --padding: 0;
    --background-color: transparent;
  }

  .segments {
    display: flex;
    flex-flow: column;
    gap: 16px;
    margin-top: 16px;
  }

  .segment {
    display: grid;
    grid-template-columns: 16px max-content 1fr;
    gap: 8px 12px;
    align-items: center;
  }

  .circle {
    display: block;
    width: 16px;
    height: 16px;
    border: var(--color-common-light-strong) 1px solid;
    border-radius: 50%;
  }

  .line {
    justify-self: center;
    width: 0;
    height: 24px;
    border-right: var(--color-main-neutral-500) 1px solid;
  }

  em {
    color: var(--color-main-neutral-500);
  }

  .fare-rules {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }

  .fare-rules > button {
    color: var(--color-common-light-text-link);
    text-decoration: underline;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
