<script lang="ts" context="module">
  import Tabs, { type Tab } from "components/ui/tabs.svelte";

  type ViewId = "all" | "cancellations" | "refunds";

  const tabs: Record<ViewId, Tab> = {
    all: { url: routeConfig.tripManagement.orders.root, label: "All", exact: true },
    cancellations: {
      url: routeConfig.tripManagement.orders.cancellations.root,
      label: "Cancellations",
      exact: true,
    },
    refunds: { url: routeConfig.tripManagement.orders.refunds.root, label: "Refunds", exact: true },
  };

  export const departureAtDateRange = writable<DateRange | undefined>(undefined);
  export const createdAtDateRange = writable<DateRange | undefined>(undefined);
  export const searchQuery = writable("");
</script>

<script lang="ts">
  import FilterIcon from "components/icons/filter-icon.svelte";
  import { slide } from "svelte/transition";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SearchField from "components/ui/search-field.svelte";
  import routeConfig from "routeConfig";
  import { writable } from "svelte/store";
  import type { DateRange } from "models/date-time";
  import Button from "components/ui/button.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";

  let showFilters = false;

  $: filtersActive = Boolean($createdAtDateRange || $departureAtDateRange);

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

<div class="header">
  <h1 class="typography headline-medium bold">Orders</h1>

  <div class="actions">
    <SearchField bind:value={$searchQuery} />

    <button on:click={toggleFilters}>
      <FilterIcon color="var(--color-main-primary-500)" active={filtersActive} />
    </button>

    <Button size="small" href={routeConfig.tripManagement.book.root}>
      New Order
      <PlusIcon />
    </Button>
  </div>
</div>

<div class="tabs">
  {#if showFilters}
    <ul class="filters" transition:slide={{ duration: 250 }}>
      <li>
        <DatePicker
          bind:value={$departureAtDateRange}
          label="Departure date"
          range
          placeholder="Date Range"
        />
      </li>
      <li>
        <DatePicker
          bind:value={$createdAtDateRange}
          label="Created date"
          range
          placeholder="Date Range"
        />
      </li>
    </ul>
  {/if}

  <Tabs items={Object.values(tabs)} />
</div>

<div class="content">
  <slot />
</div>

<style>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32px 24px;
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

  .filters :global(.date-picker) {
    --height: 40px;
    --label-font-family: "Inter";
    --label-font-size: 14px;
    --label-font-weight: 600;

    width: 100%;
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }
</style>
