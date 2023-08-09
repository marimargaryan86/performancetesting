<script lang="ts">
  import BookingSteps from "../booking-steps.svelte";
  import SearchForm, { type BookingSearchData } from "../search-form.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import Checkbox from "../checkbox.svelte";
  import TimeRange from "./time-range.svelte";
  import JourneyDuration from "./journey-duration.svelte";
  import RailwayOperators from "./railway-operators.svelte";
  import Button from "components/ui/button.svelte";
  import Offer, { type OfferModel } from "./offer.svelte";
  import { fade } from "svelte/transition";
  import offersMock from "../offers-mockup";
  import { onMount } from "svelte";
  import routeConfig from "routeConfig";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";

  export let offers: OfferModel[] = offersMock;

  let searchData: Partial<BookingSearchData> = {};

  function toggleSelectedOffer(event: CustomEvent<{ id: number }>): void {
    offers.forEach(function (offer) {
      offer.alternativeFares.forEach(function (fare) {
        fare.selected = false;
      });
      if (offer.id === event.detail.id) {
        offer.selected = !offer.selected;
      } else {
        offer.selected = false;
      }
    });
    offers = offers;
  }

  let searchQuery: string;
  let currentBookingStep = 2;

  const sortByFields = [
    "Lowest price",
    "Fastest",
    "Earlier departure",
    "Later departure",
    "Earlier arrival",
    "Latest arrival",
  ];

  let sortBy = "";
  let offerSelected = false;
  let isFareSelected = false;
  let selectedFare: OfferModel["alternativeFares"][number] | undefined = undefined;

  $: {
    offerSelected = offers.some((offer) => offer.selected === true);
    isFareSelected = false;
  }

  function handleFareSelected(
    event: CustomEvent<OfferModel & { fare: OfferModel["alternativeFares"][number] }>,
  ): void {
    isFareSelected = event.detail.selected;

    let urlParams = $page.url.searchParams;

    if (isFareSelected) {
      selectedFare = event.detail.fare;
      urlParams.set("fare_id", selectedFare.id.toString());
      urlParams.set("offer_id", event.detail.id.toString());
    } else {
      selectedFare = undefined;
      urlParams.delete("fare_id");
      urlParams.delete("offer_id");
    }

    searchQuery = urlParams.toString();
  }

  function cancelSelectedOffer(): void {
    offers.forEach(function (offer) {
      offer.selected = false;
      offer.alternativeFares.forEach(function (fare) {
        fare.selected = false;
      });
    });
    offers = offers;
    offerSelected = false;
    isFareSelected = false;
  }

  function goToSummaryPage(): void {
    goto(`${routeConfig.book.passengerDetails.root}?${searchQuery}`);
  }

  onMount(() => {
    const urlParams = $page.url.searchParams;
    searchQuery = urlParams.toString();

    searchData.adults = Number(urlParams.get("adults")) ?? 0;
    searchData.children = Number(urlParams.get("children")) ?? 0;
    searchData.infants = Number(urlParams.get("infants")) ?? 0;
    searchData.origin = urlParams.get("origin") ?? "";
    searchData.destination = urlParams.get("destination") ?? "";
    searchData.outbound = new Date(Number(urlParams.get("from"))) ?? undefined;
  });
</script>

<svelte:head>
  <title>Book · Junction Hub</title>
</svelte:head>

<div class="book typography body-large">
  <h1 class="typography headline-medium bold container header">Select an offer</h1>

  <BookingSteps currentStep={currentBookingStep} />
  <SearchForm data={searchData} firstStep={currentBookingStep === 1} />

  <div class="background">
    <div class="wrapper typography body-medium">
      <div class="left flex-gap">
        <div class="left-content flex-gap">
          <div class="flex-gap">
            <h3>Sort by</h3>
            <div class="sort-by">
              <SelectField placeholder="Select" options={sortByFields} bind:value={sortBy} />
            </div>
          </div>
          <div class="stops">
            <h3>Stops</h3>
            <Checkbox label="Direct" checked />
            <Checkbox label="Non-stop" />
            <Checkbox label="Indirect" />
          </div>
          <hr />
          <div class="flex-gap">
            <h3>Departure time</h3>
            <TimeRange label="Departure" />
            <TimeRange label="Arrival" />
          </div>
          <hr />
          <div class="flex-gap">
            <h3>Journey Duration</h3>
            <JourneyDuration />
          </div>
          <hr />
          <div class="flex-gap">
            <h3>Railway Operators</h3>
            <RailwayOperators />
          </div>
        </div>
      </div>
      <div class="right">
        {#each offers as offer (offer.id)}
          <Offer
            {offer}
            on:toggleSelectedOffer={toggleSelectedOffer}
            on:fareSelected={handleFareSelected}
          />
        {/each}
      </div>
    </div>
  </div>
  {#if offerSelected}
    <div class="next-block" transition:fade={{ duration: 100 }}>
      <Button on:click={cancelSelectedOffer} size="medium" variant="outline">Cancel</Button>
      <Button on:click={goToSummaryPage} size="medium" disabled={!isFareSelected}
        ><span class="next-btn">Next</span></Button
      >
    </div>
  {/if}
</div>

<style>
  .book {
    position: relative;
    align-self: center;
    width: 100%;
    height: 100%;
    border-radius: 16px 16px 0 0;
  }

  .wrapper .left .sort-by :global(.wrapper) {
    height: 40px;
  }

  h3 {
    margin-bottom: 8px;
  }

  hr {
    width: 100%;
    border: none;
    border-top: 1px solid var(--color-common-line-medium);
  }

  .stops {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 24px;
  }

  .background {
    min-height: 100%;
    padding: 24px 0;
    background: var(--color-gradient-booking-flow);
  }

  .container {
    margin: 0 24px;
  }

  .header {
    padding-top: 16px;
  }

  h1 {
    margin-bottom: 16px;
  }

  .left {
    position: sticky;
    top: 0;
    width: 30%;
    height: 100lvh;
    margin: 0 16px 0 24px;
    overflow-y: hidden;
    color: #28231b;
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .left-content {
    padding: 16px 24px;
    overflow-y: scroll;
  }

  .left .left-content::-webkit-scrollbar {
    width: 5px;
  }

  .left .left-content::-webkit-scrollbar-thumb {
    height: 101px;
    background-color: var(--color-main-neutral-300);
    border-radius: 4px;
  }

  .left .left-content::-webkit-scrollbar-track {
    background-color: var(--color-main-neutral-50);
  }

  .right {
    width: 100%;
    margin-right: 16px;
    overflow: hidden;
  }

  .wrapper {
    display: flex;
    flex-direction: row;
  }

  .flex-gap {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .next-block {
    position: sticky;
    bottom: 0;
    display: flex;
    gap: 16px;
    align-items: flex-end;
    align-self: stretch;
    justify-content: end;
    width: 100%;
    padding: 16px 24px;
    background-color: var(--color-common-dark-strong);
  }

  .next-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100px;
  }
</style>
