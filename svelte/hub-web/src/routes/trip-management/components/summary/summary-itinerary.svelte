<script lang="ts">
  import { formatDuration } from "$lib/formatting/date-time";
  import { getTimeDeltaS } from "~/utils/date-time";
  import Collapsible from "../collapsible.svelte";
  import { createEventDispatcher } from "svelte";
  import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import EntityAvatar from "~/components/ui/entity-avatar.svelte";
  import { getLegsFromPriceQuote } from "~/utils/offer";
  import { getLocale, getTranslator } from "~/i18n";

  export let priceQuote: TripOfferPriceQuote;

  const locale = getLocale();
  const t = getTranslator();

  $: vendor = priceQuote.options[0]?.detailsList[0]?.details?.vendor ?? $t("words.unknown");
  $: trainNumber = priceQuote.options[0]?.detailsList[0]?.details?.routeIdentifiers.vendor ?? "";
  $: stopCount = (priceQuote.options[0]?.detailsList.length ?? 1) - 1;
  $: departureLeg = priceQuote.options[0]?.detailsList[0]?.details?.legs[0];

  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }

  $: legs = getLegsFromPriceQuote(priceQuote);
</script>

<Collapsible class="itinerary" title={$t("words.itinerary")}>
  <div class="trip-info" typography="body-small">
    <div>
      <EntityAvatar name={vendor} size="24px" />
      {vendor}
      {trainNumber} • {$t("words.stopCounter", { count: stopCount })}
    </div>
    <span>
      {#if departureLeg}
        {departureLeg.departureAt.toLocaleDateString($locale, {
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
      <li class="segment" typography="label-large" weight="bold">
        <span class="circle" />
        <strong>
          {leg.departureAt.toLocaleTimeString($locale, {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: leg.origin.timeZone,
          })}
        </strong>
        <strong>{leg.origin.name}</strong>

        <span class="line" />
        <em typography="body-small" weight="default">
          {formatDuration(getTimeDeltaS(leg.departureAt, leg.arrivalAt))}
        </em>
        <em />

        <span class="circle" />
        <strong>
          {leg.arrivalAt.toLocaleTimeString($locale, {
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
    <button typography="body-small" on:click={showFareRules}>
      {$t("actions.viewFareRules")}
    </button>
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
