<script lang="ts">
  import BookingSteps from "../booking-steps.svelte";
  import SearchForm from "../search-form.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import Check from "../check.svelte";
  import TimeRange from "./time-range.svelte";
  import JourneyDuration from "./journey-duration.svelte";
  import RailwayOperators from "./railway-operators.svelte";
  import Button from "components/ui/button.svelte";
  import Offer from "./offer.svelte";
  import { fade } from "svelte/transition";
  import OffersMockup from "./offers-mockup.ts";
  import type { BookingSearchForm } from "../booking-search-form";
  import { onMount } from "svelte";

  let bookingSearchForm = {} as BookingSearchForm;
  export let offers = OffersMockup;

  function toggleSelectedOffer(event): void {
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

  onMount(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);

    bookingSearchForm.adults = Number(urlParams.get("adults")) ?? 0;
    bookingSearchForm.children = Number(urlParams.get("children")) ?? 0;
    bookingSearchForm.infants = Number(urlParams.get("infants")) ?? 0;
    bookingSearchForm.origin = urlParams.get("origin") ?? "";
    bookingSearchForm.destination = urlParams.get("destination") ?? "";
    bookingSearchForm.fromDate = new Date(Number(urlParams.get("from"))) ?? undefined;
  });

  const currentBookingStep = 2;
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
  let selectedFare = {};

  $: {
    offerSelected = offers.some((offer) => offer.selected === true);
    isFareSelected = false;
  }

  function handleFareSelected(event): void {
    isFareSelected = event.detail.selected;
    if (isFareSelected) {
      selectedFare = event.detail.fare;
    } else {
      selectedFare = {};
    }
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
</script>

<svelte:head>
  <title>Book · Junction Hub</title>
</svelte:head>

<div class="book typography body-large">
  <h1 class="typography headline-medium bold container header">Select an offer</h1>

  <BookingSteps currentStep={currentBookingStep} />
  <SearchForm {bookingSearchForm} firstStep={currentBookingStep === 1} />

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
            <Check label="Direct" isChecked />
            <Check label="Non-stop" />
            <Check label="Indirect" />
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
    <div class="next-block" transition:fade|local={{ duration: 100 }}>
      <Button on:click={cancelSelectedOffer} size="medium" variant="outline">Cancel</Button>
      <Button size="medium" disabled={!isFareSelected}><span class="next-btn">Next</span></Button>
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
