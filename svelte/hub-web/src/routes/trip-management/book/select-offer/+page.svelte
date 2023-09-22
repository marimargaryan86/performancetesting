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
      durationSpanM: { start: Math.min(...durations), end: Math.max(...durations) },
      vendors,
    };
  }

  function getOptions(
    offers: OfferModel[],
    offerId: string,
    optionIds: string[],
  ): OfferOptionModel[] {
    const options =
      offers
        .find(({ id }) => offerId === id)
        ?.groups.flatMap((group) => group.options.filter(({ id }) => optionIds?.includes(id))) ??
      [];

    return Array.from(new Set(options));
  }

  function getTotalPrice(options: OfferOptionModel[]): PriceModel {
    return options.reduce<PriceModel>(
      (prev, curr) => ({
        currency: curr.price.currency,
        amount: prev.amount + curr.price.amount,
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
  import { callAction } from "utils/common";
  import routeConfig from "routeConfig";
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment";
  import { onDestroy } from "svelte";
  import Countdown from "../countdown.svelte";
  import LoadingSkelton from "./loading-skelton.svelte";
  import type { ResourceStatus } from "integration/junction-mobile-api/schemas/common";
  import type { OfferModel, OfferOptionModel } from "integration/junction-mobile-api/schemas/offer";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { pendableCall } from "utils/pendable-call";
  import { pollableCall } from "utils/pollable-call";
  import Alert from "components/ui/alert.svelte";
  import { getSortOffersFunc } from "sorting/offer";
  import { getFilterOffersFunc } from "filters/offer";
  import { getOfferDurationM, getVendors } from "utils/offer";
  import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
  import type { SelectActionData } from "./+page.server";

  export let data;

  let selected = {
    offerId: data.searchData.offerId,
    optionIds: data.searchData.optionIds,
  };
  let offers = data.tripCandidates.offers;
  let searchOptionsSettings = getSearchOptionSettings(offers);
  let searchOptions: SearchOptionsData = {
    sortBy: "price",
    stops: [],
    arrivalSpanM: { start: 0, end: 1440 },
    departureSpanM: { start: 0, end: 1440 },
    durationM: searchOptionsSettings.durationSpanM.start,
    vendors: [],
  };

  $: if (browser && data.tripCandidates.status !== "completed") {
    pollOffers(data.tripCandidates.id);
  }
  $: sortAndFilter = getSortAndFilteringFunc(searchOptions);

  const { poll: pollOffersAux, cancel: cancelPolling } = pollableCall({
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    func(_: string) {
      return callAction<{
        status: ResourceStatus;
        offers: OfferModel[];
      }>({
        action: routeConfig.routes.tripManagement.routes.book.routes.select.actions.poll,
        apply: false,
      });
    },
    check(result) {
      if (
        result.type !== "success" ||
        result.data?.status === "unspecified" ||
        result.data?.status === "failed"
      ) {
        return { status: "done" };
      }

      if (result.data) {
        offers = result.data.offers;
      }

      if (offers.length) {
        searchOptionsSettings = getSearchOptionSettings(offers);
        searchOptions = {
          ...searchOptions,
          durationM: searchOptionsSettings.durationSpanM.start,
          vendors: [],
        };
      }

      // Sometimes the result comes back as completed with an empty set, retry if so.
      if (result.data?.status === "completed") {
        return { status: offers.length ? "done" : "retry" };
      }

      return { status: "pending" };
    },
    sleepMs: 2000,
    retries: 3,
  });

  const { pending: offersPending, func: pollOffers } = pendableCall(pollOffersAux);

  function select(event: CustomEvent<{ offerId: string; optionIds: string[] }>): void {
    selected = event.detail;
  }

  const { pending, func: selectOffer } = pendableCall(async () => {
    if (!(selected.offerId && selected.optionIds)) {
      return;
    }

    const originalPrice = getTotalPrice(getOptions(offers, selected.offerId, selected.optionIds));
    const actionData: SelectActionData = {
      offerId: selected.offerId,
      optionIds: selected.optionIds,
      originalPrice,
    };

    await callAction({
      action: routeConfig.routes.tripManagement.routes.book.routes.select.actions.select,
      data: actionData,
      dataType: "json",
    });

    await goto(routeConfig.routes.tripManagement.routes.book.routes.payment.root);
  });

  onDestroy(cancelPolling);
</script>

<svelte:head>
  <title>Select an offer · Book · Trip Management · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch data={data.searchData} />
</div>

<div class="content">
  <Countdown expiresAt={data.tripCandidates.expiresAt} show={Boolean(offers.length)} />

  <div class="scroll">
    <SearchOptions bind:data={searchOptions} settings={searchOptionsSettings} />

    <ul class="offer-result">
      {#each sortAndFilter(offers) as offer}
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

        {#if $pending}
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
