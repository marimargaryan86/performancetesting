<script lang="ts">
  // import { ChevronRight, ChevronLeft, Calendar } from "$icons/index.js";
  import { melt, createDateRangePicker } from "@melt-ui/svelte";
  import FaChevronRight from "svelte-icons/fa/FaChevronRight.svelte";
  import FaChevronLeft from "svelte-icons/fa/FaChevronLeft.svelte";
  import { weekDays } from "$lib/data/calendar";
  const {
    elements: { calendar, heading, grid, cell, prevButton, nextButton },
    states: { months, headingValue },
    helpers: { isDateDisabled, isDateUnavailable },
  } = createDateRangePicker({
    forceVisible: true,
  });
  export const returnTrip = false;
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
    width: 25px;
    display: flex;
    justify-content: center;
    border: none;
    background: none;
  }

  .weekday-label {
    color: var(--Text-Dark-Text, #1c1c1c);
    font-family: "Plus Jakarta Sans";
    font-size: 10px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    text-transform: uppercase;
  }

  .day-item {
    display: flex;
    height: 2.25rem;
    width: 2.25rem;
    cursor: pointer;
    background-color: white;
    font-size: 12px;
    justify-content: center;
    align-items: center;
  }
  .day-item[data-selected] {
    background: var(--Text-Dark-Text, #1c1c1c);
    color: white;
    border-radius: 50%;
  }
  .day-item[data-disabled] {
    color: #d8d8d8;
  }
</style>
