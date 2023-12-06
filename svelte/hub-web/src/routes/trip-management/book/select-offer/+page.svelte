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

  function getOptions(offers: OfferModel[], offerId: string, optionIds: string[]): OfferOption[] {
    const options =
      offers
        .find(({ id }) => offerId === id)
        ?.groups.flatMap((group) => group.options.filter(({ id }) => optionIds?.includes(id))) ??
      [];

    return Array.from(new Set(options));
  }

  function getTotalPrice(options: OfferOption[]): Price {
    return options.reduce<Price>(
      (prev, curr) => ({
        currency: curr.price.total.currency,
        amount: prev.amount + curr.price.total.amount,
      }),
      { currency: "EUR", amount: 0 },
    );
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
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment";
  import Countdown from "../countdown.svelte";
  import FareRulesDialog from "../../components/fare-rules-dialog.svelte";
  import LoadingSkelton from "./loading-skelton.svelte";
  import type {
    Offer as OfferModel,
    OfferOption,
  } from "integration/junction-mobile-api/schemas/offer";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Alert from "components/ui/alert.svelte";
  import { getSortOffersFunc } from "sorting/offer";
  import { getFilterOffersFunc } from "filters/offer";
  import { getOfferDurationM, getVendors } from "utils/offer";
  import type { Price } from "integration/common/schemas/price";
  import tripManagement from "../../../integration/trip-management/trip-management";
  import { onDestroy } from "svelte";
  import { writable } from "svelte/store";
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";

  export let data;

  let selected = {
    offerId: data.selectedOffer?.offerId,
    optionIds: data.selectedOffer?.optionIds,
  };
  let offers: OfferModel[] = data.offers.data;
  let searchOptionsSettings = getSearchOptionSettings(offers);
  let searchOptions: SearchOptionsData = {
    sortBy: "price",
    stops: [],
    arrivalSpanM: { start: 0, end: 1440 },
    departureSpanM: { start: 0, end: 1440 },
    durationM: searchOptionsSettings.durationSpanM.start,
    vendors: [],
  };
  let pollSignal = { cancelled: false };
  let fareRulesDialog: FareRulesDialog | undefined;
  let selectedPriceQuote: TripOfferPriceQuote | undefined = undefined;

  const offersPending = writable(false);
  const selectOfferPending = writable(false);

  $: if (browser && data.offerSearch && data.offers.status !== "completed") {
    getOffers();
  }
  $: sortAndFilter = getSortAndFilteringFunc(searchOptions);

  async function getOffers(): Promise<void> {
    if ($offersPending) {
      return;
    }

    try {
      $offersPending = true;
      offers = [];

      // Cancel any ongoing polls
      pollSignal.cancelled = true;
      pollSignal = { cancelled: false };

      for await (const offer of tripManagement.yieldOffers(pollSignal)) {
        offers = [...offers, offer];
      }

      searchOptionsSettings = getSearchOptionSettings(offers);
      searchOptions = {
        ...searchOptions,
        durationM: searchOptionsSettings.durationSpanM.start,
      };
    } finally {
      $offersPending = false;
    }
  }

  function select(event: CustomEvent<{ offerId: string; optionIds: string[] }>): void {
    if ($selectOfferPending) {
      return;
    }

    markSelection(event);
    selectOffer();
  }

  function markSelection(event: CustomEvent<{ offerId: string; optionIds: string[] }>): void {
    selected = event.detail;
  }

  async function selectOffer(): Promise<void> {
    if ($selectOfferPending) {
      return;
    }

    try {
      $selectOfferPending = true;

      if (!(selected.offerId && selected.optionIds)) {
        return;
      }

      await tripManagement.selectOffer({
        offerId: selected.offerId,
        optionIds: selected.optionIds,
        originalPrice: getTotalPrice(getOptions(offers, selected.offerId, selected.optionIds)),
      });

      await goto(routeConfig.routes.tripManagement.routes.book.routes.payment.root);
    } finally {
      $selectOfferPending = false;
    }
  }

  onDestroy(() => (pollSignal.cancelled = true));
</script>

<svelte:head>
  <title>Select an offer · Book · Trip Management · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch data={data.searchData} origin={data.origin} destination={data.destination} />
</div>

{#if selectedPriceQuote}
  <FareRulesDialog bind:this={fareRulesDialog} priceQuote={selectedPriceQuote} />
{/if}

<div class="content">
  {#if offers[0]?.expiresAt}
    <Countdown expiresAt={offers[0]?.expiresAt} show />
  {/if}

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
            on:markSelection={markSelection}
          />
        </li>
      {:else}
        {#if offers.length}
          <li>
            <Alert type="warning" dismissable={false}>
              <span class="typography body-medium">No trips matches the filter criteria</span>
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
            <span class="typography body-medium">No trips found</span>
          </Alert>
        </li>
      {/if}
    </ul>
  </div>
</div>

{#if selected.offerId && selected.optionIds}
  <div class="actions" transition:fade={{ duration: 200 }}>
    <div class="wrapper">
      <Button on:click={selectOffer} size="small">
        Next

        {#if $selectOfferPending}
          <LoadingIcon />
        {/if}
      </Button>
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

  .actions > .wrapper > :global(button) {
    width: 140px;
  }
</style>
