<script lang="ts" context="module">
  import Tabs, { type Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: "/pay/activity", label: "Transactions", exact: true },
    { url: "/pay/activity/fx", label: "FX", exact: true },
  ];
</script>

<script lang="ts">
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import type { LayoutData } from "./$types";
  import SearchIcon from "components/icons/search-icon.svelte";
  import FilterIcon from "components/icons/filter-icon.svelte";
  import { slide } from "svelte/transition";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { transactionStatus } from "models/transaction";
  import { formatTransactionStatus } from "formatting/transaction";

  export let data: LayoutData;

  let showFilters = false;
  let { dateRange, status } = data;

  $: filtersActive = Boolean($dateRange || $status.length);

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

<BreadCrumbs items={data.breadCrumbs} />

<div class="header">
  <h1 class="typography headline-medium bold">Activity</h1>

  <div class="actions">
    <button><SearchIcon color="var(--color-main-primary-500)" /></button>
    <button on:click={toggleFilters}>
      <FilterIcon color="var(--color-main-primary-500)" active={filtersActive} />
    </button>
  </div>
</div>

<div class="tabs">
  {#if showFilters}
    <ul class="filters" transition:slide|local={{ duration: 250 }}>
      <li>
        <DatePicker bind:value={$dateRange} range placeholder="Date Range" />
      </li>
      <li>
        <StatusPicker
          statuses={transactionStatus}
          bind:value={$status}
          format={formatTransactionStatus}
          placeholder="Status"
        />
      </li>
    </ul>
  {/if}
  <Tabs items={tabs} />
</div>

<div class="content">
  <slot />
</div>

<style>
  .header {
    display: flex;
    justify-content: space-between;
    padding: 8px 24px 24px;
  }

  .actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .actions > button {
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
    background-image: var(--color-gradient-extensions-horizontal);
  }
</style>
