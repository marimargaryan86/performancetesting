<script lang="ts">
  import FilterIcon from "components/icons/filter-icon.svelte";
  import { slide } from "svelte/transition";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { conversionStatus } from "models/conversion";
  import { formatConversionStatus } from "formatting/conversion";
  import SearchField from "components/ui/search-field.svelte";

  let showFilters = false;

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

<div class="header">
  <h1 class="typography headline-medium bold">Bookings</h1>

  <div class="actions">
    <SearchField />

    <button on:click={toggleFilters}>
      <FilterIcon color="var(--color-main-primary-500)" />
    </button>
  </div>
</div>

{#if showFilters}
  <div class="tabs">
    <ul class="filters" transition:slide|local={{ duration: 250 }}>
      <li>
        <DatePicker range placeholder="Date Range" />
      </li>
      <li>
        <StatusPicker
          statuses={conversionStatus}
          format={formatConversionStatus}
          placeholder="Status"
        />
      </li>
    </ul>
  </div>
{/if}

<div class="content">
  <slot />
</div>

<style>
  .header {
    display: flex;
    justify-content: space-between;
    padding: 34px 24px;
    color: var(--color-main-neutral-800);
  }

  .actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .actions > button {
    height: 40px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .tabs {
    padding: 16px 24px 0;
    background-color: var(--color-main-primary-50);
  }

  .filters {
    display: flex;
    gap: 16px;
    padding-bottom: 16px;
  }

  .filters > li {
    width: 100%;
    max-width: 276px;
  }

  .filters :global(.date-picker),
  .filters :global(.status-picker) {
    --height: 40px;

    width: 100%;
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-image: var(--color-gradient-booking-flow);
  }
</style>
