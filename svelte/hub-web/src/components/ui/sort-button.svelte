<script lang="ts">
  import SortingIcon from "components/icons/sorting-icon.svelte";
  import type { DirectionY } from "models/spatial";

  type TValue = $$Generic<string>;

  export let label: string;
  export let value: Readonly<TValue> | undefined;
  export let group: TValue | undefined = undefined;
  export let direction: DirectionY;

  $: active = value !== undefined && group !== undefined && value === group;

  function select(): void {
    if (active) {
      direction = direction === "up" ? "down" : "up";
    } else {
      direction = "down";
    }

    group = value;
  }
</script>

<button class="sort-button" on:click={select}>
  <span>{label}</span>

  <SortingIcon direction={active ? direction : undefined} />
</button>

<style>
  .sort-button {
    display: flex;
    gap: 6px;
    align-items: center;
    justify-content: flex-start;
    padding: 0;
    color: var(--color-neutral-800);
    font-weight: 600;
    font-size: 7px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
