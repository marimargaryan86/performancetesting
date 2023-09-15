<script lang="ts">
  import TripSearch, {
    type PartialTripSearchData,
  } from "../../components/trip-search/trip-search.svelte";
  import SearchOptions, { type SearchOptionsData } from "./search-options.svelte";
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
  import type { ResolvedSearchData } from "../common";
  import type { resourceStatus } from "integration/junction-mobile-api/schemas/common";
  import type { z } from "zod";
  import type { OfferModel } from "integration/junction-mobile-api/schemas/offer";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { pendableCall } from "utils/pendable-call";
  import { pollableCall } from "utils/pollable-call";

  export let data;

  let countdown: Countdown | undefined;
  let searchData = getSearchData(data.searchData);
  let searchOptions: SearchOptionsData = {
    sortBy: "price",
    stops: [],
    arrivalSpan: { start: 0, end: 1440 },
    departureSpan: { start: 0, end: 1440 },
    duration: 492,
    operators: [0, 1, 2],
  };
  let selected = data.selectedOffer;

  $: offersTask =
    browser && data.searchData.tripCandidatesSearch?.id
      ? pollOffers(data.searchData.tripCandidatesSearch.id)
      : undefined;

  function getSearchData(nextSearchData: ResolvedSearchData): PartialTripSearchData {
    return {
      destination: nextSearchData.destination,
      origin: nextSearchData.origin,
      outbound: nextSearchData.departureAfter,
      passengers: nextSearchData.passengers,
    };
  }

  const { poll: pollOffers, cancel: cancelPolling } = pollableCall({
    func(id: string) {
      return callAction<{
        status: z.infer<typeof resourceStatus>;
        offers: OfferModel[];
      }>({
        action: routeConfig.tripManagement.book.select.actions.poll,
        data: { tripCandidatesSearchId: id },
        apply: false,
      });
    },
    check(result) {
      if (
        result.type !== "success" ||
        result.data?.status === "unspecified" ||
        result.data?.status === "failed"
      ) {
        return { status: "done", data: [] };
      }

      if (result.data?.status === "completed") {
        if (result.data.offers.length) {
          countdown?.open();
        }

        return { status: result.data.offers.length ? "done" : "retry", data: result.data.offers };
      }

      return { status: "pending" };
    },
    sleepMs: 2000,
    retries: 3,
  });

  function select(event: CustomEvent<{ offerId: string; optionIds: string[] }>): void {
    selected = event.detail;
  }

  function search(event: CustomEvent<URL>): void {
    goto(event.detail);
  }

  const { pending, func: selectOffer } = pendableCall(async () => {
    await callAction({
      action: routeConfig.tripManagement.book.select.actions.select,
      data: selected,
    });

    await goto(routeConfig.tripManagement.book.payment.root);
  });

  onDestroy(cancelPolling);
</script>

<svelte:head>
  <title>Select an offer · Book · Trip Management · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch bind:data={searchData} on:search={search} />
</div>

<div class="content">
  {#if data.searchData.tripCandidatesSearch}
    <Countdown expiresAt={data.searchData.tripCandidatesSearch.expiresAt} bind:this={countdown} />
  {/if}

  <div class="scroll">
    <SearchOptions bind:data={searchOptions} />

    <ul class="offer-result">
      {#await offersTask}
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
        <li><LoadingSkelton /></li>
      {:then offers}
        {#if offers?.length}
          {#each offers as offer}
            <li>
              <Offer
                {offer}
                selected={selected?.offerId === offer.id}
                selectedOptionIds={selected?.offerId === offer.id ? selected.optionIds : undefined}
                on:select={select}
              />
            </li>
          {:else}
            <li class="no-result">No trips found</li>
          {/each}
        {:else}
          <li><LoadingSkelton /></li>
          <li><LoadingSkelton /></li>
          <li><LoadingSkelton /></li>
          <li><LoadingSkelton /></li>
        {/if}
      {/await}
    </ul>
  </div>
</div>

{#if selected}
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
