<script lang="ts" context="module">
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
  import TripSearch from "../../components/trip-search/trip-search.svelte";
  import SearchOptions, {
    type SearchOptionsData,
    type SearchOptionsSettings,
  } from "./search-options.svelte";
  import Offer from "./offer/offer.svelte";
  import routeConfig from "routeConfig";
  import { goto, invalidateAll } from "$app/navigation";
  import { fade } from "svelte/transition";
  import Countdown from "../countdown.svelte";
  import LoadingSkelton from "./loading-skelton.svelte";
  import type { Offer as OfferModel } from "integration/junction-mobile-api/schemas/offer";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Alert from "components/ui/alert.svelte";
  import { getSortOffersFunc } from "sorting/offer";
  import { getFilterOffersFunc } from "filters/offer";
  import { getOfferDurationM, getVendors } from "utils/offer";
  import { onDestroy, type ComponentEvents } from "svelte";
  import { writable } from "svelte/store";
  import { getPageTitle } from "utils/page-title";
  import { getLocaleData } from "i18n";
  import { manager, type PartialSelectedOffer } from "../../booking-flow";
  import { browser } from "$app/environment";

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

  const i18n = getLocaleData();
  const offersPending = writable(true);
  const selectOfferPending = writable(false);

  $: offerSearchId = data.bookingSession.offerSearch.id;
  $: getOffers(offerSearchId);
  $: sortAndFilter = getSortAndFilteringFunc(searchOptions);

  async function getOffers(nextOfferSearchId: string): Promise<void> {
    if (!browser) {
      return;
    }

    $offersPending = true;
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

    $offersPending = false;
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
      await goto(routeConfig.routes.tripManagement.routes.book.routes.payment.root);
    } finally {
      $selectOfferPending = false;
    }
  }

  async function search(event: ComponentEvents<TripSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    await manager.search(event.detail.data);
    await invalidateAll();
    event.detail.pending.set(false);
  }

  onDestroy(() => {
    if (browser) {
      offerPollController?.abort();
    }
  });
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.book.title,
      $i18n.pages.tripManagement.pages.book.pages.select.title,
    )}
  </title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch data={data.bookingSession.searchData} on:search={search} />
</div>

<div class="content">
  <Countdown expiresAt={data.bookingSession.offerSearch.expiresAt} show />

  <div class="scroll">
    <SearchOptions bind:data={searchOptions} settings={searchOptionsSettings} />

    <ul class="offer-result">
      {#each sortAndFilter(offers) as offer (offer.id)}
        <li>
          <Offer
            {offer}
            selected={selected.offerId === offer.id}
            selectedOptionIds={selected.offerId === offer.id ? selected.optionIds : undefined}
            on:select={select}
          />
        </li>
      {:else}
        {#if offers.length}
          <li>
            <Alert type="warning" dismissable={false}>
              <span typography="body-medium">
                {$i18n.sentences.noTripsMatchesTheFilterCriteria}
              </span>
            </Alert>
          </li>
        {/if}
      {/each}

      {#if $offersPending}
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
      {:else if !offers.length}
        <li>
          <Alert type="warning" dismissable={false}>
            <span typography="body-medium">{$i18n.sentences.noTripsFound}</span>
          </Alert>
        </li>
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
        {$i18n.actions.next}

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

  .search-wrapper > :global(.trip-search > .autocomplete-field),
  .search-wrapper > :global(.trip-search > .date-picker) {
    --height: 40px;
    --icon-size: 16px;
  }

  .search-wrapper > :global(.trip-search > button.swap) {
    margin-top: 24px;
  }

  .search-wrapper > :global(.trip-search > button) {
    height: 40px;
    padding-right: 12px;
    padding-left: 12px;
  }

  .search-wrapper > :global(.trip-search > button > svg) {
    width: 20px;
    height: 20px;
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
