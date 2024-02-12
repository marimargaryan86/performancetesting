<script lang="ts">
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { getLegsFromPriceQuote } from "$lib/utils/offer";
  import { getPassengersPresentation, type PassengerPickerData } from "$lib/models/passenger";
  import { getLocale, getTranslator } from "$lib/i18n";

  export let priceQuote: MobileSchemas.TripOfferPriceQuote;
  export let passengers: PassengerPickerData;

  const locale = getLocale();
  const t = getTranslator();

  $: legs = getLegsFromPriceQuote(priceQuote);
  $: departureLeg = legs[0];
  $: arrivalLeg = legs[legs.length - 1];
</script>

<div transition:slideFade={{ duration: 300 }} class="trip-banner" typography="body-large">
  {#if departureLeg && arrivalLeg}
    <p>
      {departureLeg.departureAt.toLocaleDateString($locale, {
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
      {getPassengersPresentation(passengers, $t)}
    </p>
  {:else}
    <p>{$t("sentences.loadingTripDetails")}</p>
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
