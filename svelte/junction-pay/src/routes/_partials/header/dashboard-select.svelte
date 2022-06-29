<script lang="ts">
  import keyBinding from "$lib/actions/key-binding";
  import { scale } from "svelte/transition";
  import DashboardOption from "./dashboard-option.svelte";

  type Option = DashboardOption["$$prop_def"]["option"];

  export let value: Option;

  const options: Option[] = ["pay", "go", "plus"];

  let expanded = false;
  let positionRelative = expanded;

  function select(option: Option): void {
    value = option;
  }

  function toggle(): void {
    expanded = !expanded;
  }

  function expand(): void {
    expanded = true;
  }

  function collapse(): void {
    expanded = false;
  }
</script>

<div
  class="dashboard-select"
  style:--position={positionRelative ? "relative" : "static"}
  use:keyBinding={{ Enter: toggle, Escape: collapse, Space: expand }}
  role="listbox"
  aria-expanded={expanded}
  tabindex="0"
  on:blur={collapse}
>
  <div class="selected" on:click={toggle} role="button">
    <DashboardOption option={value} />

    <span class="chevron" class:expanded />
  </div>

  {#if expanded}
    <ul
      class="options"
      transition:scale|local={{ duration: 150, start: 0.9 }}
      on:introstart={() => (positionRelative = true)}
      on:outroend={() => (positionRelative = false)}
    >
      {#each options as option}
        <li
          class="option"
          aria-selected={option === value}
          on:click={() => {
            select(option);
            collapse();
          }}
        >
          <DashboardOption {option} />
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .dashboard-select {
    display: inline-block;
    height: 49px;
    min-width: 196px;
    position: var(--position);
  }

  .selected {
    align-items: center;
    background-color: var(--color-white);
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    height: 100%;
    justify-content: space-between;
    padding: 0 12px;
    width: 100%;
  }

  .chevron {
    border: var(--color-gray-light) 2px solid;
    border-width: 0 2px 2px 0;
    display: block;
    height: 10px;
    transform: translateY(-2px) rotateZ(45deg);
    transition: transform 150ms ease;
    width: 10px;
  }

  .chevron.expanded {
    transform: translateY(2px) rotateZ(225deg);
  }

  .options {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 3px 3px 10px 0 rgb(0 0 0 / 10%);
    margin-top: 2px;
    padding: 6px 0;
    transform-origin: top center;
  }

  .option {
    cursor: pointer;
    padding: 12px;
  }

  .options:not(:hover) > .option[aria-selected="true"] {
    background-color: var(--color-light-background);
  }

  .option:hover {
    background-color: var(--color-light-background);
  }
</style>
