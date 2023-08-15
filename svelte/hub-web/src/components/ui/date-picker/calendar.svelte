<script lang="ts" generics="TRange extends boolean">
  /* global TRange */
  import type { DateRange } from "models/date-time";
  import { datesEq, getMonthLength, getWeekDays, getZeroTimeDate } from "utils/date-time";

  type TValue = TRange extends true ? DateRange : Date;
  type TDirtyValue = TRange extends true ? Partial<DateRange> : Date;

  export let range: TRange;
  export let value: TValue | undefined;
  export let viewingMonth: Date;

  let dirtyValue: TDirtyValue | undefined = value;

  const today = getZeroTimeDate();
  const weekDays = getWeekDays(undefined, "short");

  $: year = viewingMonth.getFullYear();
  $: month = viewingMonth.getMonth();
  $: paddingLeft = (new Date(year, month, 0).getDay() + 1) % 7;
  $: monthLength = getMonthLength(viewingMonth);
  $: paddingRight = (7 - new Date(year, month + 1, 1).getDay()) % 7;
  $: days = [
    ...[...Array(paddingLeft)].map((_, idx) => new Date(year, month, -idx)).reverse(),
    ...[...Array(monthLength)].map((_, idx) => new Date(year, month, idx + 1)),
    ...[...Array(paddingRight)].map((_, idx) => new Date(year, month + 1, idx + 1)),
  ];

  function select(date: Date): void {
    if (!range) {
      const nextValue = dirtyValue && datesEq(date, dirtyValue as Date) ? undefined : date;

      dirtyValue = nextValue as TDirtyValue;
      value = nextValue as TValue;

      return;
    }

    let nextValue = dirtyValue as Partial<DateRange> | undefined;

    if (nextValue?.from) {
      if (nextValue.to || nextValue.from > date) {
        nextValue = { from: date };
      } else {
        nextValue = { ...nextValue, to: date };
      }
    } else {
      nextValue = { from: date };
    }

    dirtyValue = nextValue as TDirtyValue;
    value = nextValue?.from && nextValue.to ? (nextValue as TValue) : undefined;
  }

  function isStart(date: Date, currValue: TDirtyValue | undefined): boolean {
    if (!range) {
      return false;
    }

    const nextValue = currValue as DateRange | undefined;

    if (!nextValue?.from || !nextValue.to) {
      return false;
    }

    return Boolean(nextValue?.from && datesEq(date, nextValue.from));
  }

  function isEnd(date: Date, currValue: TDirtyValue | undefined): boolean {
    if (!range) {
      return false;
    }

    const nextValue = currValue as DateRange | undefined;

    if (!nextValue?.from || !nextValue.to) {
      return false;
    }

    return Boolean(nextValue?.to && datesEq(date, nextValue.to));
  }

  function isInRange(date: Date, currValue: TDirtyValue | undefined): boolean {
    if (!range) {
      return false;
    }

    const nextValue = currValue as DateRange | undefined;

    if (!nextValue?.from || !nextValue.to) {
      return false;
    }

    return date < nextValue.to && nextValue.from < date;
  }

  function isSelected(date: Date, currValue: TDirtyValue | undefined): boolean {
    if (!range && currValue instanceof Date) {
      return datesEq(date, currValue);
    }

    const nextValue = currValue as DateRange | undefined;

    return (
      Boolean(nextValue?.from && datesEq(nextValue.from, date)) ||
      Boolean(nextValue?.to && datesEq(nextValue.to, date))
    );
  }
</script>

<div class="calendar typography body-small">
  {#each Object.values(weekDays) as weekDay}
    <span class="cell typography body-medium bold">{weekDay}</span>
  {/each}

  {#each days as day, idx}
    <button
      type="button"
      class="cell date"
      class:prev-month={idx < paddingLeft}
      class:next-month={idx >= days.length - paddingRight}
      class:today={datesEq(day, today)}
      class:selected={isSelected(day, dirtyValue)}
      class:in-range={isInRange(day, dirtyValue)}
      class:start={isStart(day, dirtyValue)}
      class:end={isEnd(day, dirtyValue)}
      on:click={select.bind(select, day)}
    >
      <span>{day.getDate()}</span>
    </button>
  {/each}
</div>

<style>
  .calendar {
    display: grid;
    grid-template-columns: repeat(7, 40px);
    gap: 2px 0;
    color: var(--color-main-neutral-900);
  }

  .cell {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 40px;
  }

  .date {
    position: relative;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .prev-month,
  .next-month {
    color: var(--color-main-neutral-500);
  }

  .today {
    color: var(--color-semantic-error-500);
  }

  .in-range {
    background-color: var(--color-main-primary-100);
  }

  .date.start::after {
    right: 0;
  }

  .date.end::after {
    left: 0;
  }

  .date.start:not(.end)::after,
  .date.end:not(.start)::after {
    position: absolute;
    top: 0;
    display: block;
    width: 50%;
    height: 100%;
    background-color: var(--color-main-primary-100);
    content: "";
  }

  .date > span {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    border: transparent 1px solid;
    border-radius: 50%;
  }

  .selected > span {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
  }

  .date:hover > span {
    border-color: var(--color-main-neutral-200);
  }
</style>
