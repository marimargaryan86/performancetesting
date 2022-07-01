<script lang="ts">
  import clickOutside from "$lib/actions/click-outside";
  import { scale } from "svelte/transition";
  import Button from "../button.svelte";

  export let date: Date;

  let expanded = false;

  const yearStart = new Date().getFullYear() - 50;
  const years = [...Array(100)].map((_, idx) => yearStart + idx);

  $: year = date.getFullYear().toString();

  function toggle(): void {
    expanded = !expanded;
  }

  function collapse(): void {
    expanded = false;
  }

  function scrollToSelected(ev: { currentTarget: HTMLUListElement }): void {
    const children = Array.from(ev.currentTarget.children);
    const selected = children.find((child) => child.getAttribute("aria-selected") === "true");

    selected?.scrollIntoView({ block: "center" });
  }

  function select(year: number): void {
    const date_ = new Date(date);
    date_.setFullYear(year);

    date = date_;
    collapse();
  }
</script>

<div class="year-picker" use:clickOutside={collapse}>
  <Button on:click={toggle}>{year}</Button>

  {#if expanded}
    <ul transition:scale={{ duration: 150, start: 0.9 }} on:introstart={scrollToSelected}>
      {#each years as year}
        <li aria-selected={date.getFullYear() === year} on:click={() => select(year)}>{year}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .year-picker {
    position: relative;
  }

  .year-picker > :global(button) {
    background-color: transparent;
    color: var(--color-orange);
    font-size: 20px;
    height: unset;
    padding: 0;
  }

  ul {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 0 0 15px rgb(0 0 0 / 9%);
    left: 0;
    max-height: 240px;
    overflow-y: scroll;
    padding: 12px;
    position: absolute;
    top: calc(100% + 4px);
    transform-origin: center 0;
    z-index: 2;
  }

  li[aria-selected="true"] {
    color: var(--color-orange);
  }

  ul:not(:hover) > li[aria-selected="true"] {
    background-color: var(--color-light-background);
  }

  li {
    border-radius: 5px;
    color: var(--color-gray);
    cursor: pointer;
    padding: 6px;
  }

  li:hover {
    background-color: var(--color-light-background);
  }
</style>
