<script lang="ts" context="module">
  type Direction = "earlier" | "later";
  type PendingType = Direction | "initial";
</script>

<script lang="ts">
  import {
    SEARCH_WINDOW_DELTA_MS,
    SEARCH_WINDOW_H,
    tripSearchDataParser,
  } from "$lib/components/pages/trip-management/booking-flow-train/trip-search-data";
  import SearchOptions from "$lib/components/pages/trip-management/booking-flow-train/select-offer/search-options.svelte";
  import Offer from "$lib/components/pages/trip-management/booking-flow-train/select-offer/offer/offer.svelte";
  import routeConfig from "$lib/route-config";
  import { goto, invalidateAll } from "$app/navigation";
  import LoadingSkelton from "$lib/components/pages/trip-management/booking-flow-train/select-offer/loading-skelton.svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import Alert from "$lib/components/ui/alert.svelte";
  import {
    getSearchOptionSettings,
    getSortAndFilteringFunc,
    type SearchOptionsData,
  } from "$lib/utils/offer";
  import { onDestroy, type ComponentEvents } from "svelte";
  import { writable } from "svelte/store";
  import { getTranslator } from "$lib/i18n";
  import {
    manager,
    type PartialSelectedOffer,
    type SearchData,
  } from "$lib/booking-manager/booking-manager";
  import { browser } from "$app/environment";
  import CollapsibleTripSearch from "$lib/components/pages/trip-management/booking-flow-train/trip-search/collapsible-trip-search.svelte";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";
  import OfferResultLayout from "$lib/components/pages/trip-management/offer-result-layout.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;

  let selected: PartialSelectedOffer = data.bookingSession.selectedOffer ?? {};
  let offers: MobileSchemas.Offer[] = [];
  let searchOptionsSettings = getSearchOptionSettings(offers);
  let searchOptions: SearchOptionsData = {
    sortBy: "lowest-price",
    stops: [],
    arrivalSpanM: { start: 0, end: 1440 },
    departureSpanM: { start: 0, end: 1440 },
    durationM: searchOptionsSettings.durationSpanM.start,
    vendors: [],
  };
  let offerPollController: AbortController | undefined;

  const featureTools = getFeatureTools();
  const t = getTranslator();
  const selectOfferPending = writable(false);
  let offersPending: PendingType | undefined = "initial";

  $: searchData = tripSearchDataParser.fromSearchData(data.bookingSession.searchData);
  $: offerSearchId = data.bookingSession.offerSearch.id;
  $: getOffers(offerSearchId);
  $: sortAndFilter = getSortAndFilteringFunc(searchOptions);

  async function getOffers(nextOfferSearchId: string): Promise<void> {
    if (!browser) {
      return;
    }

    offers = [];
    offerPollController?.abort();
    offerPollController = new AbortController();

    for await (const offer of manager.getOffers(nextOfferSearchId, offerPollController.signal)) {
      offers = [...offers, offer];
    }

    searchOptionsSettings = getSearchOptionSettings(offers);
    searchOptions = {
      ...searchOptions,
      durationM: searchOptionsSettings.durationSpanM.start,
    };

    const prevOffersPending = offersPending;
    offersPending = undefined;

    if (offers.length) {
      autoFetchMore(prevOffersPending);
    }
  }

  async function select(event: ComponentEvents<Offer>["select"]): Promise<void> {
    if ($selectOfferPending) {
      return;
    }

    const { proceed, ...nextSelected } = event.detail;
    selected = nextSelected;

    if (!proceed) {
      return;
    }

    try {
      $selectOfferPending = true;

      const offer = offers.find((item) => item.id === selected.offerId);
      const options = offer?.groups
        .flatMap((item) => item.options)
        .filter((item) => selected.optionIds?.includes(item.id));

      if (!(offer && options?.length)) {
        return;
      }

      await manager.selectOffer(data.bookingSession, offer, options);
      await goto(routeConfig.routes.tripManagement.routes.book.routes.rail.routes.payment.root);
    } finally {
      $selectOfferPending = false;
    }
  }

  async function search(
    pendingType: PendingType,
    event: ComponentEvents<CollapsibleTripSearch>["search"],
  ): Promise<void> {
    event.detail.pending.set(true);
    await searchAux(pendingType, event.detail.data);
    event.detail.pending.set(false);
  }

  async function searchAux(pendingType: PendingType, nextData: SearchData): Promise<void> {
    offers = [];
    offersPending = pendingType;
    await manager.search(nextData, $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS));
    await invalidateAll();
  }

  async function fetchMore(direction: Direction): Promise<void> {
    if (offersPending) {
      return;
    }

    const nextOutbound = new Date(data.bookingSession.searchData.outbound);
    nextOutbound.setHours(
      nextOutbound.getHours() + (direction === "earlier" ? -SEARCH_WINDOW_H : SEARCH_WINDOW_H),
    );

    data.bookingSession.searchData = {
      ...data.bookingSession.searchData,
      outbound: nextOutbound,
    };

    await searchAux(direction, data.bookingSession.searchData);
  }

  function autoFetchMore(pendingType: PendingType | undefined): void | Promise<void> {
    if (!pendingType || pendingType === "initial") {
      return;
    }

    if (
      pendingType === "earlier" &&
      data.bookingSession.searchData.outbound.getHours() < SEARCH_WINDOW_H
    ) {
      return;
    }

    if (
      pendingType === "later" &&
      data.bookingSession.searchData.outbound.getHours() > 23 - SEARCH_WINDOW_H
    ) {
      return;
    }

    return fetchMore(pendingType);
  }

  // Hide earlier button if search window is in the past
  $: showEarlierButton =
    data.bookingSession.searchData.outbound.getTime() - new Date().getTime() >
    SEARCH_WINDOW_DELTA_MS;
  $: showLaterButton = true;

  onDestroy(() => {
    if (browser) {
      offerPollController?.abort();
    }
  });
</script>

<OfferResultLayout
  showActions={Boolean(selected.offerId && selected.optionIds)}
  pageTitle={$t("pages.tripManagement.pages.book.pages.rail.pages.select.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.rail.pages.select.subTitle")}
  expiresAt={data.bookingSession.offerSearch.expiresAt}
  showCountdown={Boolean(offers.length)}
>
  <CollapsibleTripSearch
    {searchData}
    on:search={search.bind(search, "initial")}
    slot="search-drawer"
  />

  <SearchOptions bind:data={searchOptions} settings={searchOptionsSettings} slot="search-options" />

  <ul class="offer-result">
    {#if $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS)}
      {#if showEarlierButton}
        <li class="earlier">
          <button on:click={fetchMore.bind(fetchMore, "earlier")} disabled={Boolean(offersPending)}>
            <span typography="label-medium" weight="bold">
              {$t("words.earlier")}
            </span>
            {#if offersPending === "earlier"}
              <LoadingIcon color="var(--color-common-light-text-link)" size="16px" />
            {:else}
              <ChevronIcon direction="up" color="var(--color-common-light-text-link)" />
            {/if}
          </button>
        </li>
      {/if}
    {/if}

    {#each sortAndFilter(offers) as offer (offer.id)}
      <li>
        <Offer
          {offer}
          selected={selected.offerId === offer.id}
          selectedOptionIds={selected.offerId === offer.id ? selected.optionIds : undefined}
          pending={$selectOfferPending}
          on:select={select}
        />
      </li>
    {:else}
      {#if offers.length}
        <li>
          <Alert type="warning" dismissable={false}>
            <span typography="body-medium">
              {$t("sentences.noTripsMatchesTheFilterCriteria")}
            </span>
          </Alert>
        </li>
      {/if}
    {/each}

    {#if offersPending}
      <li><LoadingSkelton /></li>
      <li><LoadingSkelton /></li>
      <li><LoadingSkelton /></li>
      <li><LoadingSkelton /></li>
    {:else if !offers.length}
      <li>
        <Alert type="warning" dismissable={false}>
          <span typography="body-medium">{$t("sentences.noTripsFound")}</span>
        </Alert>
      </li>
    {/if}

    {#if $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS)}
      {#if showLaterButton}
        <li class="later">
          <button on:click={fetchMore.bind(fetchMore, "later")} disabled={Boolean(offersPending)}>
            <span typography="label-medium" weight="bold">
              {$t("words.later")}
            </span>
            {#if offersPending === "later"}
              <LoadingIcon color="var(--color-common-light-text-link)" size="16px" />
            {:else}
              <ChevronIcon direction="down" color="var(--color-common-light-text-link)" />
            {/if}
          </button>
        </li>
      {/if}
    {/if}
  </ul>

  <svelte:fragment slot="actions">
    {#if selected.offerId && selected.optionIds}
      <button
        on:click={select.bind(
          select,
          new CustomEvent("search", {
            detail: { proceed: true, offerId: selected.offerId, optionIds: selected.optionIds },
          }),
        )}
        variant="primary"
        size="small"
        class="action"
      >
        {$t("actions.next")}

        {#if $selectOfferPending}
          <LoadingIcon />
        {/if}
      </button>
    {/if}
  </svelte:fragment>
</OfferResultLayout>

<style>
  .offer-result {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-self: flex-start;
    width: 100%;
    max-width: var(--result-width);
  }

  .earlier > button,
  .later > button {
    display: flex;
    gap: 4px;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 16px;
    color: var(--color-common-light-text-link);
    background-color: var(--color-common-background-light-main);
    border-color: transparent;
    border-radius: 16px;
    cursor: pointer;
    transition: background-color 300ms ease;
  }

  .earlier > button:hover,
  .later > button:hover {
    background-color: var(--color-common-background-light-hover);
  }

  button.action {
    width: 140px;
  }
</style>
