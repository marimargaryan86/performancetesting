<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { monthName } from "formatting/date-time";
  import type { DateRange } from "models/date-time";
  import { scale } from "svelte/transition";
  import { getZeroTimeDate } from "utils/date-time";
  import Calendar from "./calendar.svelte";

  type TRange = $$Generic<boolean>;
  type TValue = TRange extends true ? DateRange : Date;

  export let range: TRange;
  export let value: TValue | undefined;

  let viewingMonth = getViewingMonth();
  let month = viewingMonth.getMonth();
  let year = viewingMonth.getFullYear();

  $: viewingMonth = new Date(year, month, 1);

  function getViewingMonth(): Date {
    if (range) {
      const currValue = value as DateRange | undefined;

      return currValue?.from ?? getZeroTimeDate();
    }

    return (value ?? getZeroTimeDate()) as Date;
  }

  function goToNext(): void {
    let nextMonth = month + 1;

    if (nextMonth > 11) {
      nextMonth = 0;
      year++;
    }

    month = nextMonth;
  }

  function goToPrev(): void {
    let nextMonth = month - 1;

    if (nextMonth < 0) {
      nextMonth = 11;
      year--;
    }

    month = nextMonth;
  }
</script>

<div class="dialogue" transition:scale|local={{ duration: 150, start: 0.8 }}>
  <div class="header">
    <div class="typography body-large bold">
      {monthName(viewingMonth)}
      {viewingMonth.getFullYear()}
    </div>

    <div class="navigation">
      <button class="navigate" type="button" on:click={goToPrev}>
        <ChevronIcon direction="left" color="var(--color-main-neutral-900)" />
      </button>

      <button class="navigate" type="button" on:click={goToNext}>
        <ChevronIcon direction="right" color="var(--color-main-neutral-900)" />
      </button>
    </div>
  </div>

  <Calendar {viewingMonth} {range} bind:value />
</div>

<style>
  .dialogue {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 100;
    margin-top: 4px;
    padding: 20px;
    color: var(--color-main-neutral-900);
    background: #ffffff;
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgb(17 24 39 / 0.05), 0 12px 16px rgb(17 24 39 / 0.1);
    transform-origin: top left;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 20px;
    white-space: nowrap;
    border-bottom: var(--color-main-neutral-200) 1px solid;
  }

  .navigation {
    display: flex;
    gap: 8px;
  }

  .navigate {
    padding: 0;
    background: transparent;
    border: 0;
    cursor: pointer;
  }

  .navigate > :global(svg) {
    width: 20px;
    height: 20px;
    vertical-align: top;
  }
</style>
