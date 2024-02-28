<script lang="ts">
  import { formatDuration } from "$lib/formatting/date-time";
  import { getTimeDeltaS } from "$lib/utils/date-time";
  import Collapsible from "../../collapsible.svelte";
  import { createEventDispatcher } from "svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import EntityAvatar from "$lib/components/ui/entity-avatar.svelte";
  import { getLegsAndSequencesFromPriceQuote } from "$lib/utils/offer";
  import { getLocale, getTranslator } from "$lib/i18n";

  export let priceQuote: MobileSchemas.TripOfferPriceQuote;
  export let isRoundTrip: boolean;

  const locale = getLocale();
  const t = getTranslator();

  $: vendor = priceQuote.options[0]?.detailsList[0]?.details?.vendor ?? $t("words.unknown");
  $: trainNumber = priceQuote.options[0]?.detailsList[0]?.details?.routeIdentifiers.vendor ?? "";
  $: stopCount = (priceQuote.options[0]?.detailsList.length ?? 1) - 1;
  $: departureLeg = priceQuote.options[0]?.detailsList[0]?.details?.legs[0];

  // TODO: Double check that these are the correct options
  $: vendorInbound = priceQuote.options[1]?.detailsList[0]?.details?.vendor ?? $t("words.unknown");
  $: trainNumberInbound =
    priceQuote.options[1]?.detailsList[0]?.details?.routeIdentifiers.vendor ?? "";
  $: stopCountInbound = (priceQuote.options[1]?.detailsList.length ?? 1) - 1;
  $: departureLegInbound = priceQuote.options[1]?.detailsList[0]?.details?.legs[0];

  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }

  $: legsAndSequences = getLegsAndSequencesFromPriceQuote(priceQuote);

  $: outboundLegs = legsAndSequences
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .filter(([_leg, sequence]) => sequence === 1)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .map(([leg, _sequence]) => leg);

  $: inboundLegs = legsAndSequences
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .filter(([_leg, sequence]) => sequence === 2)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    .map(([leg, _sequence]) => leg);
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
    {#if isRoundTrip}
      <h2 typography="body-small" weight="bold">{$t("words.outbound")}</h2>
    {/if}
    {#each outboundLegs as leg}
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

    {#if isRoundTrip}
      <hr />
      <div class="trip-info" typography="body-small">
        <div>
          <EntityAvatar name={vendorInbound} size="24px" />
          {vendorInbound}
          {trainNumberInbound} • {$t("words.stopCounter", { count: stopCountInbound })}
        </div>
        <span>
          {#if departureLegInbound}
            {departureLegInbound.departureAt.toLocaleDateString($locale, {
              month: "long",
              day: "numeric",
              year: "numeric",
              timeZone: departureLegInbound.origin.timeZone,
            })}
          {/if}
        </span>
      </div>

      <h2 typography="body-small" weight="bold">{$t("words.inbound")}</h2>

      {#each inboundLegs as leg}
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
    {/if}
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

  hr {
    width: 100%;
    border: solid 1px var(--color-common-dark-medium);
  }
</style>
