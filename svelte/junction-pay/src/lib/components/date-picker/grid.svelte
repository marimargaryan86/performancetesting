<script lang="ts">
  import keyBinding from "$lib/actions/key-binding";
  import utils from "$lib/utils";

  export let focusedMonth: Date;
  export let selectedStart: Date | undefined = undefined;
  export let selectedEnd: Date | undefined = undefined;
  export let span: boolean;

  let end: Date;
  let startPadding: undefined[] = [];
  let endPadding: undefined[] = [];

  $: start = new Date(focusedMonth);
  $: {
    end = new Date(start);
    end.setMonth(end.getMonth() + 1);
    end.setDate(0);
    end = end;
  }
  $: startPadding = [...Array(utils.getWeekDay(start))].map(() => undefined);
  $: endPadding = [...Array(6 - utils.getWeekDay(end))].map(() => undefined);
  $: days = [...Array(end.getDate())].map((_, idx) => {
    const date = new Date(end);
    date.setDate(idx + 1);

    return date;
  });
  $: grid = [...startPadding, ...days, ...endPadding];

  function select(day: Date): void {
    if (!span) {
      selectedStart = day;
      selectedEnd = day;
      return;
    }

    if (selectedStart && !selectedEnd && day < selectedStart) {
      selectedStart = day;
      return;
    }

    if (!selectedStart || selectedEnd) {
      selectedStart = day;
      selectedEnd = undefined;
    } else {
      selectedEnd = day;
    }
  }
</script>

<div class="grid">
  {#each utils.weekDays as weekDay}
    <span class="header">{weekDay}</span>
  {/each}

  {#each grid as day}
    {@const selected =
      (selectedStart && day && utils.compareDates(selectedStart, day) === 0) ||
      (selectedEnd && day && utils.compareDates(selectedEnd, day) === 0)}
    {@const start =
      selected &&
      selectedStart &&
      selectedEnd &&
      utils.compareDates(day, selectedStart) === 0 &&
      utils.compareDates(selectedStart, selectedEnd) !== 0}
    {@const end =
      selected &&
      selectedStart &&
      selectedEnd &&
      utils.compareDates(day, selectedEnd) === 0 &&
      utils.compareDates(selectedStart, selectedEnd) !== 0}
    {@const span = selectedStart && selectedEnd && day && day > selectedStart && day < selectedEnd}

    <span
      tabindex={!day ? -1 : 0}
      class="day"
      class:empty={!day}
      class:start
      class:end
      class:span
      aria-selected={selected}
      on:click={!day ? undefined : () => select(day)}
      use:keyBinding={{ Enter: () => day && select(day), Space: () => day && select(day) }}
    >
      {#if day}
        <span>{day.getDate()}</span>
      {/if}
    </span>
  {/each}
</div>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(7, calc(100% / 7));
    text-align: center;
    width: 100%;
  }

  .header {
    color: var(--color-gray-lighter);
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .day {
    cursor: pointer;
    height: 43px;
    margin-top: 6px;
    padding: 4px;
    position: relative;
  }

  .day > span {
    align-items: center;
    border: transparent 1px solid;
    border-radius: 50%;
    color: var(--color-orange);
    display: flex;
    font-size: 18px;
    height: 100%;
    justify-content: center;
    position: relative;
    width: 100%;
    z-index: 1;
  }

  .day:hover > span {
    border-color: var(--color-orange);
  }

  .day.start::after,
  .day.end::after,
  .day.span::after {
    background-color: var(--color-orange-light);
    content: "";
    display: block;
    height: calc(100% - 8px);
    position: absolute;
    top: 4px;
    width: 50%;
  }

  .day.start::after {
    right: 0;
  }

  .day.end::after {
    left: 0;
  }

  .day.span > span {
    border-color: transparent;
  }

  .day.span::after {
    left: 0;
    width: 100%;
  }

  .day[aria-selected="true"] > span {
    background-color: var(--color-orange);
    border-color: transparent;
    color: var(--color-white);
    font-weight: 600;
  }

  .empty {
    cursor: default;
  }
</style>
