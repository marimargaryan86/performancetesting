<script lang="ts">
  import AlternativeFare from "./alternative-fare.svelte";
  import Chevron from "components/icons/chevron-icon.svelte";
  import { createEventDispatcher } from "svelte";
  import type { OfferModel } from "../offer.svelte";

  const dispatch = createEventDispatcher();

  export let alternativeFares: OfferModel["alternativeFares"];
  export let offerId: number;

  function toggleSelectedFare(event: CustomEvent<{ id: number }>): void {
    alternativeFares.forEach(function (fare) {
      if (fare.id === event.detail.id) {
        fare.selected = !fare.selected;
        dispatch("fareSelected", { offerId, fare, selected: fare.selected });
      } else {
        fare.selected = false;
      }
    });
    alternativeFares = alternativeFares;
  }

  function scrollToRight(): void {
    const container = document.getElementById("fares-slider");

    if (container) {
      container.scrollLeft += 168;
    }
  }

  function scrollToLeft(): void {
    const container = document.getElementById("fares-slider");

    if (container) {
      container.scrollLeft -= 168;
    }
  }

  function handleKeyScrollToRight(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      scrollToRight();
    }
  }

  function handleKeyScrollToLeft(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      scrollToLeft();
    }
  }
</script>

<div class="wrapper">
  <div class="slider" id="fares-slider">
    {#each alternativeFares as alternativeFare}
      <AlternativeFare
        on:toggleSelectedFare={toggleSelectedFare}
        {alternativeFare}
        bind:selected={alternativeFare.selected}
      />
    {/each}
  </div>

  <button class="prev" on:click={scrollToLeft} on:keyup={handleKeyScrollToLeft}>
    <Chevron direction="left" size="24px" color="var(--color-main-primary-500)" />
  </button>

  <button class="next" on:click={scrollToRight} on:keyup={handleKeyScrollToRight}>
    <Chevron size="24px" color="var(--color-main-primary-500)" />
  </button>
</div>

<style>
  .wrapper {
    position: relative;
    padding: 18px 40px 0;
  }

  .prev,
  .next {
    position: absolute;
    top: 50%;
    padding: 8px;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .prev {
    left: 0;
  }

  .next {
    right: 0;
  }

  .slider {
    display: flex;
    gap: 8px;
    overflow: scroll;
    scroll-behavior: smooth;
    transition: scroll-left 0.4s ease-in-out;
  }

  .slider::-webkit-scrollbar {
    display: none;
  }
</style>
