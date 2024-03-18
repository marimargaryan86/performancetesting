<script lang="ts">
  import { createDatePicker, melt } from "@melt-ui/svelte";
  import { CalendarDate } from "@internationalized/date";
  import type { SelectedDate } from "$lib/models/common";
  import Icon from "./icon.svelte";

  const {
    elements: { calendar, cell, grid, heading, nextButton, prevButton },
    states: { months, headingValue, weekdays, value },
    helpers: { isDateDisabled, isDateUnavailable },
  } = createDatePicker({
    forceVisible: true,
    defaultValue: new CalendarDate(2024, 1, 11),
  });

  export let selectedDate: SelectedDate = {};

  $: selectedDate = {
    date: $value ? $value.toString() : "",
  };
</script>

<div use:melt={$calendar}>
  <header class="calendar-heading">
    <button class="month-button" use:melt={$prevButton}>
      <Icon variant="chevron-left" />
    </button>
    <div use:melt={$heading}>
      {$headingValue}
    </div>
    <button class="month-button" use:melt={$nextButton}>
      <Icon variant="chevron-right" />
    </button>
  </header>
  <div>
    {#each $months as month}
      <table use:melt={$grid}>
        <thead aria-hidden="true">
          <tr>
            {#each $weekdays as day}
              <th>
                <div class="weekday-label">
                  {day}
                </div>
              </th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each month.weeks as weekDates}
            <tr>
              {#each weekDates as date}
                <td
                  role="gridcell"
                  aria-disabled={$isDateDisabled(date) || $isDateUnavailable(date)}
                >
                  <div
                    class="day-item"
                    data-selected="false"
                    data-disabled="false"
                    use:melt={$cell(date, month.value)}
                  >
                    {date.day}
                  </div>
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    {/each}
  </div>
</div>

<style>
  .calendar-heading {
    display: flex;
    justify-content: space-between;
    padding-bottom: 20px;
  }

  .month-button {
    display: flex;
    justify-content: center;
    width: 25px;
    background: none;
    border: none;
  }

  .weekday-label {
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 400;
    font-size: 10px;
    text-transform: uppercase;
  }

  .day-item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    font-size: 12px;
    background-color: white;
    cursor: pointer;
  }

  .day-item[data-selected] {
    color: white;
    background: var(--text-dark-text, #1c1c1c);
    border-radius: 50%;
  }

  .day-item[data-disabled] {
    color: #d8d8d8;
  }
</style>
