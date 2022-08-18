<script lang="ts">
  import clickOutside from "$lib/actions/click-outside";
  import utils from "$lib/utils";
  import { scale } from "svelte/transition";
  import Button from "../button.svelte";
  import TextField from "../text-field.svelte";
  import Grid from "./grid.svelte";
  import Header from "./header.svelte";

  export let id: string | undefined = undefined;
  export let start: Date | undefined = undefined;
  export let end: Date | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let span = false;
  export let error = false;

  let container: HTMLDivElement;
  let focusedMonth = utils.setZeroTime(start ? new Date(start) : new Date());
  let expanded = false;

  $: start = start ? utils.setZeroTime(start) : undefined;
  $: end = end ? utils.setZeroTime(end) : undefined;
  $: displayValue =
    (start ? utils.formatDate(start, 1) : "") +
    (span && end ? ` - ${utils.formatDate(end, 1)}` : "");
  $: {
    focusedMonth.setDate(1);
    focusedMonth = new Date(focusedMonth);
  }

  $: if (expanded) {
    updateFocusedMonth();
  }

  function updateFocusedMonth(): void {
    focusedMonth = utils.setZeroTime(start ? new Date(start) : new Date());
  }

  function reset(): void {
    start = undefined;
    end = undefined;
  }

  function toggle(): void {
    expanded = !expanded;
  }

  function collapse(): void {
    if (span && start && !end) {
      end = new Date(start);
    }

    expanded = false;
  }

  function blur(e: FocusEvent): void {
    if (!container.contains(e.relatedTarget as Node)) {
      collapse();
    }
  }
</script>

<div class="date-picker" use:clickOutside={collapse} bind:this={container} class:error>
  <TextField
    {id}
    value={displayValue}
    {placeholder}
    readOnly
    on:click={toggle}
    on:blur={blur}
    {error}
  />

  {#if expanded}
    <div class="calendar" transition:scale|local={{ duration: 150, start: 0.9 }}>
      <Header bind:focusedMonth />

      <Grid {focusedMonth} bind:selectedStart={start} bind:selectedEnd={end} {span} />

      <Button on:click={reset}>Reset</Button>
    </div>
  {/if}
</div>

<style>
  .date-picker {
    border-radius: 10px;
    display: inline-block;
    font-size: 14px;
    height: 44px;
    position: relative;
  }

  .date-picker.error {
    border-color: var(--color-red);
  }

  .calendar > :global(button) {
    background-color: transparent;
    color: var(--color-black);
    height: unset;
    padding: 2px;
  }

  .date-picker > :global(.text-field) {
    border-radius: inherit;
    font-size: inherit;
    height: 100%;
    width: 100%;
  }

  .calendar {
    background-color: var(--color-white);
    border-radius: 10px;
    box-shadow: 0 10px 60px rgb(0 0 0 / 10%);
    display: grid;
    gap: 16px;
    grid-template-rows: max-content max-content max-content;
    left: 0;
    padding: 18px 16px;
    position: absolute;
    top: calc(100% + 9px);
    transform-origin: center 0;
    width: 340px;
    z-index: 1;
  }
</style>
