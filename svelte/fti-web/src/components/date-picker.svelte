<script lang="ts">
  import { createDatePicker, melt } from "@melt-ui/svelte";
  import { CalendarDate } from "@internationalized/date";
  import FaChevronRight from "svelte-icons/fa/FaChevronRight.svelte";
  import FaChevronLeft from "svelte-icons/fa/FaChevronLeft.svelte";

  const {
    elements: { calendar, cell, grid, heading, nextButton, prevButton },
    states: { months, headingValue, weekdays },
    helpers: { isDateDisabled, isDateUnavailable },
  } = createDatePicker({
    forceVisible: true,
    defaultValue: new CalendarDate(2024, 1, 11),
  });
</script>

<div use:melt={$calendar}>
  <header class="calendar-heading">
    <button class="month-button" use:melt={$prevButton}>
      <FaChevronLeft size={24} />
    </button>
    <div use:melt={$heading}>
      {$headingValue}
    </div>
    <button class="month-button" use:melt={$nextButton}>
      <FaChevronRight size={24} />
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
