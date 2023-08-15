<script lang="ts">
  import TripSearch, { type PartialTripSearchData } from "../trip-search.svelte";
  import { page } from "$app/stores";
  import SearchOptions, { type SearchOptionsData } from "./search-options.svelte";
  import type { OfferModel } from "models/booking/offer";
  import Offer from "./offer/offer.svelte";
  import { callAction, sleep } from "utils/common";
  import routeConfig from "routeConfig";
  import type { TripCandidatesSearchStatus } from "integration/junction-mobile-api/schemas/trip";
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import { fade } from "svelte/transition";
  import { browser } from "$app/environment";
  import { onDestroy } from "svelte";
  import type { MaybePromise } from "@sveltejs/kit";
  import Countdown from "../countdown.svelte";

  export let data;

  let countdown: Countdown | undefined;
  let getOffersTask: MaybePromise<OfferModel[]> = [];
  let searchData = getSearchData($page.url);
  let searchOptions: SearchOptionsData = {
    sortBy: "price",
    stops: [],
    arrivalSpan: { start: 0, end: 1440 },
    departureSpan: { start: 0, end: 1440 },
    duration: 492,
    operators: [0, 1, 2],
  };
  let searchRetries = 0;
  let selected = data.selectedOffer;

  $: tripCandidatesSearchId = data.tripCandidatesSearch?.id;
  $: if (browser && tripCandidatesSearchId) {
    beginPoll(tripCandidatesSearchId);
  }

  function beginPoll(id: string): void {
    searchRetries = 0;
    countdown?.close();
    getOffersTask = pollOffers(id);
  }

  function getSearchData(url: URL): PartialTripSearchData {
    const outboundStr = url.searchParams.get("outbound") ?? undefined;

    return {
      destination: data.destination,
      origin: data.origin,
      outbound: outboundStr ? new Date(outboundStr) : undefined,
      passengers: {
        adults: Number(url.searchParams.get("adults") ?? 1),
        children: Number(url.searchParams.get("children") ?? 0),
        infants: Number(url.searchParams.get("infants") ?? 0),
      },
    };
  }

  async function pollOffers(id: string): Promise<OfferModel[]> {
    if (tripCandidatesSearchId !== id) {
      return [];
    }

    const result = await callAction<{ status: TripCandidatesSearchStatus; offers: OfferModel[] }>({
      action: routeConfig.book.select.actions.poll,
      data: { tripCandidatesSearchId: id },
      apply: false,
    });

    if (result.type !== "success") {
      return [];
    }

    if (result.data?.status === "unspecified" || result.data?.status === "failed") {
      return [];
    }

    if (result.data?.status === "completed") {
      if (result.data.offers.length) {
        countdown?.open();
      }

      if (result.data.offers.length || searchRetries >= 3) {
        return result.data.offers;
      }

      searchRetries++;
    }

    await sleep(2000);

    return pollOffers(id);
  }

  function select(event: CustomEvent<{ offerId: string; optionIds: string[] }>): void {
    selected = event.detail;
  }

  function search(event: CustomEvent<URL>): void {
    goto(event.detail);
  }

  async function goToNext(): Promise<void> {
    await callAction({
      action: routeConfig.book.select.actions.select,
      data: selected,
    });

    goto(routeConfig.book.passengerDetails.root);
  }

  onDestroy(() => (tripCandidatesSearchId = undefined));
</script>

<svelte:head>
  <title>Select an offer · Book · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch bind:data={searchData} on:search={search} />
</div>

<div class="content">
  {#if data.tripCandidatesSearch}
    <Countdown expiresAt={data.tripCandidatesSearch.expiresAt} bind:this={countdown} />
  {/if}

  <div class="scroll">
    <SearchOptions bind:data={searchOptions} />

    <ul class="offer-result">
      {#await getOffersTask}
        <li class="pending">Searching for trips</li>
      {:then offers}
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
      {/await}
    </ul>
  </div>
</div>

{#if selected}
  <div class="actions" transition:fade={{ duration: 200 }}>
    <Button on:click={goToNext} size="small">Next</Button>
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
    width: 52px;
    height: 40px;
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
    display: flex;
    justify-content: flex-end;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
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

  .actions > :global(button) {
    width: 140px;
  }
</style>
