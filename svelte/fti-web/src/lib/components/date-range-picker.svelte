<script lang="ts">
  import { melt, createDateRangePicker } from "@melt-ui/svelte";
  import FaChevronRight from "svelte-icons/fa/FaChevronRight.svelte";
  import FaChevronLeft from "svelte-icons/fa/FaChevronLeft.svelte";
  import { weekDays } from "$lib/data/calendar";
  import type { SelectedDate } from "$lib/models/common";
  const {
    elements: { calendar, heading, grid, cell, prevButton, nextButton },
    states: { months, headingValue, value },
    helpers: { isDateDisabled, isDateUnavailable },
  } = createDateRangePicker({
    forceVisible: true,
  });
  export const returnTrip = false;

  export let selectedDate: SelectedDate = {};

  $: selectedDate = {
    start: $value.start?.toString(),
    end: $value.end?.toString(),
  };
</script>

<div>
  <div use:melt={$calendar}>
    <header class="calendar-heading">
      <button class="month-button" use:melt={$prevButton}><FaChevronLeft /> </button>
      <div use:melt={$heading}>
        {$headingValue}
      </div>
      <button class="month-button" use:melt={$nextButton}>
        <FaChevronRight />
      </button>
    </header>
    <div>
      {#each $months as month}
        <table use:melt={$grid}>
          <thead aria-hidden="true">
            <tr>
              {#each weekDays as day}
                <th>
                  <div class="weekday-label">
                    {day.slice(0, 3)}
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
                      data-disabled="false"
                      data-selected="false"
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
