<script lang="ts">
  import { formatDuration } from "formatting/date-time";
  import { getTimeDeltaS } from "utils/date-time";
  import Collapsible from "../collapsible.svelte";
  import { createEventDispatcher } from "svelte";
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import { getLegsFromPriceQuote } from "utils/offer";

  export let priceQuote: TripOfferPriceQuote;

  $: vendor = priceQuote.options[0]?.detailsList[0]?.details?.vendor ?? "Unknown";
  $: trainNumber = priceQuote.options[0]?.detailsList[0]?.details?.routeIdentifiers.vendor ?? "";
  $: segmentCount = priceQuote.options[0]?.detailsList.length ?? 1;
  $: departureLeg = priceQuote.options[0]?.detailsList[0]?.details?.legs[0];

  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }

  $: legs = getLegsFromPriceQuote(priceQuote);
</script>

<Collapsible class="itinerary" title="Itinerary">
  <div class="trip-info typography body-small">
    <div>
      <EntityAvatar name={vendor} size="24px" />
      {vendor}
      {trainNumber} • {segmentCount === 1 ? "Direct" : `${segmentCount} stops`}
    </div>
    <span>
      {#if departureLeg}
        {departureLeg.departureAt.toLocaleDateString("en-GB", {
          month: "long",
          day: "numeric",
          year: "numeric",
          timeZone: departureLeg.origin.timeZone,
        })}
      {/if}
    </span>
  </div>

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
    <button class="typography body-small" on:click={showFareRules}>View fare rules</button>
  </div>
</Collapsible>

<style>
  :global(.collapsible.itinerary) {
    --border-radius: 0;
    --padding: 0;
    --background-color: transparent;
  }

  .trip-info {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .trip-info > div {
    display: flex;
    gap: 8px;
    align-items: center;
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
