<script lang="ts">
  import { clickOutside } from "$lib/directives";
  import EyeDropperIcon from "$lib/icons/eye-dropper-icon.svelte";
  import { onMount } from "svelte";
  import { fly } from "svelte/transition";
  import Map from "../map.svelte";
  import TextInput from "./text-input.svelte";

  export let latitude: number = undefined;
  export let longitude: number = undefined;

  let pickerVisible = false;
  let pickerContainer: HTMLDivElement;
  let observer: IntersectionObserver;

  $: coordinates = !isNaN(latitude) && !isNaN(longitude) ? { latitude, longitude } : undefined;

  $: if (observer) {
    if (pickerContainer) {
      observer.observe(pickerContainer);
    } else {
      observer.disconnect();
    }
  }

  onMount(() => {
    function keyDown(e: KeyboardEvent): void {
      if (e.code === "Escape") {
        pickerVisible = false;
      }
    }

    function intersect(e: IntersectionObserverEntry[]): void {
      const target = e[0].target as HTMLDivElement;

      if (e[0].isIntersecting) {
        return;
      }

      if (e[0].boundingClientRect.right > e[0].rootBounds.width) {
        target.style.right = "0px";
        target.style.left = undefined;
      } else {
        target.style.right = undefined;
        target.style.left = "0px";
      }
    }

    window.addEventListener("keydown", keyDown);

    observer = new IntersectionObserver(intersect, {
      root: document,
      rootMargin: "0px",
      threshold: 1.0,
    });

    return () => {
      observer.disconnect();
      window.removeEventListener("keydown", keyDown);
    };
  });
</script>

<div class="coordinates-input" use:clickOutside={() => (pickerVisible = false)}>
  <TextInput bind:value={latitude} label="Latitude" type="number" min={-90} max={90} />

  <TextInput bind:value={longitude} label="Longitude" type="number" min={-180} max={180} />

  <button
    type="button"
    on:click={() => (pickerVisible = !pickerVisible)}
    title="Select coordinates from map"
  >
    <EyeDropperIcon />
  </button>

  {#if pickerVisible}
    <div
      class="picker"
      transition:fly={{ y: -12, opacity: 0, duration: 150 }}
      bind:this={pickerContainer}
    >
      <Map
        on:selectPoint={(e) => ({ latitude, longitude } = e.detail)}
        center={coordinates}
        markers={coordinates ? [{ coordinates }] : []}
      />
    </div>
  {/if}
</div>

<style>
  .coordinates-input {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr max-content;
    gap: 8px;
  }

  button {
    background-color: transparent;
    align-self: center;
    border: 0;
    padding: 2px;
    margin: 0;
    fill: var(--color-teal-dark);
    cursor: pointer;
    outline: 0;
    border-radius: 4px;
  }

  button:focus {
    box-shadow: var(--focus-outline);
  }

  .picker {
    overflow: hidden;
    background-color: var(--color-white);
    box-shadow: var(--focus-outline);
    border-radius: 4px;
    position: absolute;
    z-index: 1;
    top: calc(100% + 8px);
    width: 600px;
    height: 400px;
  }

  .picker > :global(.map) {
    width: 100%;
    height: 100%;
  }
</style>
