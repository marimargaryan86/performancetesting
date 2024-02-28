<script lang="ts">
  import type { PartialSelectedOfferData } from "$lib/booking-manager/booking-manager";
  import { SEARCH_WINDOW_H, type TripType } from "../../search/trip-search-data";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import LoadingSkeleton from "./loading-skeleton.svelte";
  import OfferGroup from "./offer-group.svelte";
  import { createEventDispatcher, type ComponentEvents } from "svelte";
  import type { Writable } from "svelte/store";
  import { sleep } from "$lib/utils/common";
  import { fade } from "svelte/transition";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { flip } from "svelte/animate";
  import { getTranslator } from "$lib/i18n";
  import { cubicInOut } from "svelte/easing";
  import type { OfferFilterFunc } from "$lib/filters/offer";
  import type { OfferSortFunc } from "$lib/sorting/offer";
  import { getGroups, getOffer } from "$lib/utils/offer";
  import type { TimeWindowDirection, TripDirection } from "$lib/models/trip";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import Alert from "$lib/components/ui/alert.svelte";
  import Icon from "$lib/components/icons/icon.svelte";

  const featureTools = getFeatureTools();
  const t = getTranslator();
  const dispatch = createEventDispatcher<{
    createpricequote: Writable<boolean>;
    movetimewindow: TimeWindowDirection;
  }>();

  export let pending: boolean;
  export let offers: MobileSchemas.Offer[];
  export let selected: PartialSelectedOfferData;
  export let tripType: TripType;
  export let tripDate: Date;
  export let tripDirection: TripDirection;
  export let sort: OfferSortFunc;
  export let filter: OfferFilterFunc;

  let delay = tripType === "round-trip" ? sleep(2000) : undefined;

  $: groups = getGroups(
    offers,
    tripType,
    tripDirection === "inbound" ? selected.outbound?.id : undefined,
  );

  function createPriceQuote(priceQuotePending: Writable<boolean>): void {
    dispatch("createpricequote", priceQuotePending);
  }

  function select(proceed: boolean, event: ComponentEvents<OfferGroup>["select"]): void {
    selected[tripDirection] = event.detail.option;

    selected.offer = getOffer({
      offers,
      tripType,
      outbound: selected.outbound,
      inbound: selected.inbound,
    });

    // Remove inbound option if it doesn't exist within the offer
    if (!selected.offer && selected.inbound) {
      selected.inbound = undefined;
    }

    if (proceed) {
      if (tripDirection === "outbound" && tripType === "round-trip") {
        tripDirection = "inbound";
      } else {
        createPriceQuote(event.detail.pending);
      }
    }
  }

  function moveTimeWindow(direction: TimeWindowDirection): void {
    dispatch("movetimewindow", direction);
    timeWindowDirection = direction;
  }

  let timeWindowDirection: TimeWindowDirection | undefined = undefined;
  $: if (!pending) {
    timeWindowDirection = undefined;
  }

  $: earlierDisabled = Boolean(
    pending || timeWindowDirection || tripDate.getHours() < SEARCH_WINDOW_H,
  );
  $: laterDisabled = Boolean(
    pending || timeWindowDirection || tripDate.getHours() + SEARCH_WINDOW_H > 23,
  );
  $: earlierIconColor = earlierDisabled
    ? "var(--color-main-neutral-700)"
    : "var(--color-common-light-text-link)";
  $: laterIconColor = laterDisabled
    ? "var(--color-main-neutral-700)"
    : "var(--color-common-light-text-link)";
</script>

<div class="offer-list" style:--rows={tripType === "round-trip" ? "max-content 1fr" : "1fr"}>
  {#if tripType === "round-trip"}
    <h3 typography="headline-medium">
      {#if tripDirection === "outbound"}
        <!-- eslint-disable svelte/no-at-html-tags -->
        {@html $t("pages.tripManagement.pages.book.pages.rail.pages.select.outbound")}
      {:else}
        {@html $t("pages.tripManagement.pages.book.pages.rail.pages.select.inbound")}
        <!-- eslint-enable svelte/no-at-html-tags -->
      {/if}
    </h3>
  {/if}

  {#await delay}
    <div class="delay">
      <strong typography="body-large">
        {#if tripDirection === "outbound"}
          {$t("pages.tripManagement.pages.book.pages.rail.pages.select.findingOutbound")}
        {:else}
          {$t("pages.tripManagement.pages.book.pages.rail.pages.select.findingInbound")}
        {/if}

        <LoadingIcon color="var(--color-main-primary-700)" />
      </strong>
    </div>
  {:then}
    <ul in:fade={{ duration: 300 }}>
      {#if $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS)}
        <li>
          <button
            class="move-time-window"
            typography="body-large"
            weight="bold"
            disabled={earlierDisabled}
            on:click={moveTimeWindow.bind(moveTimeWindow, "earlier")}
          >
            {$t("words.earlier")}

            {#if timeWindowDirection === "earlier"}
              <LoadingIcon color={earlierIconColor} size="16px" />
            {/if}

            <ChevronIcon direction="up" color={earlierIconColor} />
          </button>
        </li>
      {/if}

      {#if !groups.length}
        {#if !pending}
          <li>
            <Alert dismissable={false} type="warning">
              <Icon variant="alert-triangle" color="var(--color-semantic-warning-600)" />
              <span typography="body-medium">{$t("sentences.noTripsFound")}</span>
            </Alert>
          </li>
        {/if}
      {:else}
        {#each groups.filter(filter).toSorted(sort) as group (group.id)}
          <li animate:flip={{ duration: 600, easing: cubicInOut }}>
            <OfferGroup
              {group}
              on:select={select.bind(select, true)}
              on:mark={select.bind(select, false)}
              selectedOption={tripDirection === "outbound" ? selected.outbound : selected.inbound}
              finalSelection={tripType === "one-way" || tripDirection === "inbound"}
            />
          </li>
        {:else}
          <li>
            <Alert dismissable={false} type="warning">
              <Icon variant="alert-triangle" color="var(--color-semantic-warning-600)" />
              <span typography="body-medium">
                {$t("sentences.noTripsMatchesTheFilterCriteria")}
              </span>
            </Alert>
          </li>
        {/each}
      {/if}

      {#if pending}
        <!-- eslint-disable-next-line @typescript-eslint/no-unused-vars -->
        {#each Array.from(Array(Math.max(1, 4 - offers.length))) as _, idx (idx)}
          <li animate:flip={{ duration: 600, easing: cubicInOut }}><LoadingSkeleton /></li>
        {/each}
      {/if}

      {#if $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS)}
        <button
          class="move-time-window"
          typography="body-large"
          weight="bold"
          disabled={laterDisabled}
          on:click={moveTimeWindow.bind(moveTimeWindow, "later")}
        >
          {$t("words.later")}

          {#if timeWindowDirection === "later"}
            <LoadingIcon color={laterIconColor} size="16px" />
          {/if}

          <ChevronIcon direction="down" color={laterIconColor} />
        </button>
      {/if}
    </ul>
  {/await}
</div>

<style>
  .offer-list {
    display: grid;
    grid-template-rows: var(--rows);
    width: 100%;
    max-width: 840px;
    height: 100%;
    overflow: hidden;
    color: var(--color-common-light-strong);
  }

  h3 {
    height: 48px;
    padding: 0 16px;
  }

  .delay {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .delay > strong {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 2px 2px 10px rgb(0 0 0 / 0.2);
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 8px;
    width: 100%;
    height: 100%;
    padding: 0 16px 24px 0;
    overflow-y: auto;
    scrollbar-width: thin;
  }

  .move-time-window {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 12px;
    color: var(--color-common-light-text-link);
    background-color: var(--color-common-background-light-main);
    border: 0;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    transition: background-color 150ms ease;
  }

  .move-time-window:hover {
    background-color: var(--color-common-background-light-green);
    cursor: pointer;
  }

  .move-time-window:disabled {
    color: var(--color-main-neutral-700);
    background-color: var(--color-main-neutral-100);
  }
</style>
