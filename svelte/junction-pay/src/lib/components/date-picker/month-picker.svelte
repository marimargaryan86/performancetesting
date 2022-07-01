<script lang="ts">
  import clickOutside from "$lib/actions/click-outside";
  import utils from "$lib/utils";
  import { scale } from "svelte/transition";
  import Button from "../button.svelte";

  export let date: Date;

  $: month = date.toLocaleDateString("en-GB", { month: "long" });

  let expanded = false;

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

  function select(month: string): void {
    const date_ = new Date(date);
    date_.setMonth(utils.months.indexOf(month));

    date = date_;
    collapse();
  }
</script>

<div class="month-picker" use:clickOutside={collapse}>
  <Button on:click={toggle}>{month}</Button>

  {#if expanded}
    <ul transition:scale={{ duration: 150, start: 0.9 }} on:introstart={scrollToSelected}>
      {#each utils.months as month_}
        <li aria-selected={month_ === month} on:click={() => select(month_)}>{month_}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .month-picker {
    position: relative;
  }

  .month-picker > :global(button) {
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
