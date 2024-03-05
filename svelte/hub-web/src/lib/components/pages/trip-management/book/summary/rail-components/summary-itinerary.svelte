<script lang="ts">
  import Collapsible from "../../collapsible.svelte";
  import { createEventDispatcher } from "svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { getTranslator } from "$lib/i18n";
  import Itinerary from "$lib/components/pages/trip-management/book/select-offer/rail-components/itinerary.svelte";
  import type { TripOfferGroupDetails } from "~/integration/junction-mobile-api/schemas/offer";

  export let priceQuote: MobileSchemas.TripOfferPriceQuote;

  const t = getTranslator();

  // TODO(2024-03-04/asantos): Verify this logic
  $: outboundDetails = priceQuote.options[1]?.detailsList.map(
    ({ details }) => details,
  ) as unknown as TripOfferGroupDetails[];
  $: inboundDetails = priceQuote.options[0]?.detailsList.map(
    ({ details }) => details,
  ) as unknown as TripOfferGroupDetails[];

  const dispatch = createEventDispatcher<{ showFareRules: void }>();

  function showFareRules(): void {
    dispatch("showFareRules");
  }
</script>

<Collapsible class="itinerary" title={$t("words.itinerary")}>
  <div class="trip-info" typography="body-small">
    {#if outboundDetails !== undefined}
      <Itinerary detailsList={[...outboundDetails]} />
    {/if}
    <hr />
    {#if inboundDetails !== undefined}
      <Itinerary detailsList={[...inboundDetails]} />
    {/if}
    <div class="fare-rules">
      <button typography="body-small" on:click={showFareRules}>
        {$t("actions.viewFareRules")}
      </button>
    </div>
  </div></Collapsible
>

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
    border: 1px solid var(--color-common-dark-medium);
  }
</style>
