<script lang="ts" context="module">
  type Direction = "earlier" | "later";
  type PendingType = Direction | "initial";

  function getSortAndFilteringFunc(
    options: SearchOptionsData,
  ): (offers: OfferModel[]) => OfferModel[] {
    return (offers): OfferModel[] =>
      offers.filter(getFilterOffersFunc(options)).sort(getSortOffersFunc(options));
  }

  function getSearchOptionSettings(offers?: OfferModel[]): SearchOptionsSettings {
    if (!offers?.length) {
      return { durationSpanM: { start: 0, end: 0 }, vendors: [] };
    }

    const durations = offers.map((item) => getOfferDurationM(item));
    const vendors = Array.from(new Set(offers.flatMap((item) => getVendors(item))));

    return {
      durationSpanM: {
        start: durations.length ? Math.min(...durations) : 0,
        end: durations.length ? Math.max(...durations) : 0,
      },
      vendors,
    };
  }
</script>

<script lang="ts">
  import TripSearch, {
    SEARCH_WINDOW_DELTA_MS,
    SEARCH_WINDOW_H,
    type SearchData,
  } from "../../../components/trip-search/trip-search.svelte";
  import SearchOptions, {
    type SearchOptionsData,
    type SearchOptionsSettings,
  } from "./search-options.svelte";
  import Offer from "./offer/offer.svelte";
  import routeConfig from "~/route-config";
  import { goto, invalidateAll } from "$app/navigation";
  import { fade } from "svelte/transition";
  import Countdown from "../countdown.svelte";
  import LoadingSkelton from "./loading-skelton.svelte";
  import type { Offer as OfferModel } from "~/integration/junction-mobile-api/schemas/offer";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import Alert from "~/components/ui/alert.svelte";
  import { getSortOffersFunc } from "~/sorting/offer";
  import { getFilterOffersFunc } from "~/filters/offer";
  import { getOfferDurationM, getVendors } from "~/utils/offer";
  import { onDestroy, type ComponentEvents } from "svelte";
  import { writable } from "svelte/store";
  import { getPageTitle } from "~/utils/page-title";
  import { getTranslator } from "~/i18n";
  import { manager, type PartialSelectedOffer } from "../../../booking-flow";
  import { browser, dev } from "$app/environment";
  import CollapsibleTripSearch from "../../../components/trip-search/collapsible-trip-search.svelte";
  import ChevronIcon from "~/components/icons/chevron-icon.svelte";

  export let data;

  let selected: PartialSelectedOffer = data.bookingSession.selectedOffer ?? {};
  let offers: OfferModel[] = [];
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

  const t = getTranslator();
  const selectOfferPending = writable(false);
  let offersPending: PendingType | undefined = "initial";

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

    offersPending = undefined;
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
      await goto(routeConfig.routes.tripManagement.routes.book.routes.train.routes.payment.root);
    } finally {
      $selectOfferPending = false;
    }
  }

  async function search(
    pendingType: PendingType,
    event: ComponentEvents<TripSearch>["search"],
  ): Promise<void> {
    event.detail.pending.set(true);
    await searchAux(pendingType, event.detail.data);
    event.detail.pending.set(false);
  }

  async function searchAux(pendingType: PendingType, nextData: SearchData): Promise<void> {
    offers = [];
    offersPending = pendingType;
    await manager.search(nextData);
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

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.book.title"),
      $t("pages.tripManagement.pages.book.pages.select.title"),
    )}
  </title>
</svelte:head>

<div class="search-wrapper">
  <CollapsibleTripSearch searchData={data.bookingSession.searchData}>
    <TripSearch data={data.bookingSession.searchData} on:search={search.bind(search, "initial")} />
  </CollapsibleTripSearch>
</div>

<div class="content">
  <Countdown expiresAt={data.bookingSession.offerSearch.expiresAt} show />

  <div class="scroll">
    <SearchOptions bind:data={searchOptions} settings={searchOptionsSettings} />
    <ul class="offer-result">
      {#if dev}
        <!-- TODO(2024-02-02/mekwall): Remove dev flag when feature goes live -->
        {#if showEarlierButton}
          <li class="earlier">
            <button
              on:click={fetchMore.bind(fetchMore, "earlier")}
              disabled={Boolean(offersPending)}
            >
              <span typography="label-medium" weight="bold">
                {$t("pages.tripManagement.pages.book.pages.select.earlier")}
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

      {#if dev}
        <!-- TODO(2024-02-02/mekwall): Remove dev flag when feature goes live -->
        {#if showLaterButton}
          <li class="later">
            <button on:click={fetchMore.bind(fetchMore, "later")} disabled={Boolean(offersPending)}>
              <span typography="label-medium" weight="bold">
                {$t("pages.tripManagement.pages.book.pages.select.later")}
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
  </div>
</div>

{#if selected.offerId && selected.optionIds}
  <div class="actions" transition:fade={{ duration: 200 }}>
    <div class="wrapper">
      <button
        on:click={select.bind(
          select,
          new CustomEvent("search", {
            detail: { proceed: true, offerId: selected.offerId, optionIds: selected.optionIds },
          }),
        )}
        variant="primary"
        size="small"
      >
        {$t("actions.next")}

        {#if $selectOfferPending}
          <LoadingIcon />
        {/if}
      </button>
    </div>
  </div>
{/if}

<style>
  .search-wrapper {
    position: relative;
    background-color: #ffffff;
  }

  .search-wrapper::after {
    position: absolute;
    top: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(180deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .content {
    --options-width: 240px;
    --result-width: calc(1152px - var(--options-width) - 72px);

    display: flex;
    flex-flow: column;
    flex-grow: 1;
    width: 100%;
    padding-top: 24px;
    overflow: auto;
  }

  .content > :global(.countdown) {
    max-width: 1104px;
    margin: 0 24px 24px;
  }

  .scroll {
    --options-width: 240px;
    --result-width: calc(1152px - var(--options-width) - 72px);

    display: flex;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    padding: 0 24px 24px;
    overflow: auto;
  }

  .scroll > :global(.search-options) {
    position: sticky;
    top: 0;
    left: 0;
    flex-shrink: 0;
    width: var(--options-width);
  }

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

  .actions {
    position: relative;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    max-width: 1104px;
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .actions > .wrapper > button {
    width: 140px;
  }
</style>
