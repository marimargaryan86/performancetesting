<script lang="ts" context="module">
  type CreateDatePicker = ReturnType<typeof createDatePicker>;
</script>

<script lang="ts">
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import { isToday, getLocalTimeZone } from "@internationalized/date";
  import { createDatePicker, melt } from "@melt-ui/svelte";

  export let elements: Pick<
    CreateDatePicker["elements"],
    "calendar" | "cell" | "grid" | "heading" | "nextButton" | "prevButton"
  >;
  export let states: Pick<CreateDatePicker["states"], "months" | "headingValue" | "weekdays">;
  export let helpers: Pick<
    CreateDatePicker["helpers"],
    "isDateDisabled" | "isDateUnavailable" | "isDateSelected"
  >;

  const { calendar, cell, grid, heading, nextButton, prevButton } = elements;
  const { months, headingValue, weekdays } = states;
  const { isDateDisabled, isDateUnavailable, isDateSelected } = helpers;
  const timeZone = getLocalTimeZone();
</script>

<div use:melt={$calendar}>
  <header>
    <button use:melt={$prevButton} type="button" class="navigation">
      <ChevronIcon direction="left" size="20px" />
    </button>
    <div use:melt={$heading} typography="title-small">{$headingValue}</div>
    <button use:melt={$nextButton} type="button" class="navigation">
      <ChevronIcon direction="right" size="20px" />
    </button>
  </header>

  {#each $months as month}
    <table use:melt={$grid}>
      <thead aria-hidden="true" class="weekdays">
        <tr>
          {#each $weekdays as day}
            <th>{day}</th>
          {/each}
        </tr>
      </thead>

      <tbody typography="body-xlarge">
        {#each month.weeks as days}
          <tr>
            {#each days as date}
              {@const disabled = Boolean($isDateDisabled(date) || $isDateUnavailable(date))}
              {@const selected = $isDateSelected(date)}

              <td role="gridcell" aria-disabled={disabled}>
                <div
                  use:melt={$cell(date, month.value)}
                  class="day"
                  class:disabled
                  class:selected
                  class:today={isToday(date, timeZone)}
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

<style>
  header {
    display: flex;
    justify-content: space-between;
    padding: 14px 0;
  }

  .navigation {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .weekdays {
    font-weight: 500;
    font-size: 12px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    letter-spacing: 0.36px;
  }

  .weekdays th {
    padding: 4px 0;
  }

  .day {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 46px;
    border-radius: 50%;
    cursor: pointer;
  }

  .day.today {
    color: var(--color-semantic-error-600);
  }

  .day:not(.disabled, .selected):hover {
    color: var(--color-main-primary-500);
  }

  .day.disabled {
    color: var(--color-main-neutral-500);
  }

  .day.selected {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
  }
</style>
