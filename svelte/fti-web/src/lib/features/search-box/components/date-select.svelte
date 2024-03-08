<script lang="ts">
  import { getSearchOptionsCtx } from "$lib/stores/search-box.store";
  import FaRegCalendarAlt from "svelte-icons/fa/FaRegCalendarAlt.svelte";
  import { setDropdown } from "$lib/helpers/common";
  import CalendarSelect from "$lib/features/search-component/calendar-select.svelte";
  import { clickOutside } from "$lib/helpers/click-outside";

  export const returnTrip: boolean = false;
  let dropdown: string = "";
  const handleSetDropdown = (value: string): string => (dropdown = setDropdown(value));
  const clickOutsideHandler = (): string => handleSetDropdown("");
  const searchOptions = getSearchOptionsCtx();
</script>

<div class="search-section date-section" use:clickOutside={clickOutsideHandler}>
  <button class="label date-label" on:click={handleSetDropdown.bind(handleSetDropdown, "date")}>
    <div class="label-container">
      <div class="icon">
        <FaRegCalendarAlt />
      </div>
      <p>Travel Dates</p>
    </div>
    <p class="desc">
      {!$searchOptions.dates || $searchOptions.dates.start === undefined
        ? "Select your date"
        : `${$searchOptions.dates?.start} - ${$searchOptions.dates?.end}`}
    </p>
  </button>
  {#if dropdown === "date"}
    <CalendarSelect returnTrip={true} bind:value={$searchOptions.dates} />
  {/if}
</div>

<style>
  .search-section {
    position: relative;
    display: flex;
    flex-basis: 22.5%;
    gap: 30px;
    align-items: center;
    margin: 0 10px;
    margin-bottom: 12px;
    border-right: 1px solid #1c1c1c;
  }

  .label-container {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .label {
    margin: 0;
    padding: 0;
  }

  .label p {
    margin: 0;
    color: var(--text-dark-text);
  }

  p.desc {
    padding: 6px 0;
    color: var(--text-grey-text, #818181);
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
  }

  .date-label {
    background: none;
    border: none;
  }

  @media only screen and (width <= 720px) {
    .search-section {
      margin: 0;
      padding: 10px 16px;
      background: #fafafa;
      border: 1px solid #eae9e9;
      border-radius: 4px;
    }

    :global(.dropdown) {
      z-index: 99;
    }
  }
</style>
