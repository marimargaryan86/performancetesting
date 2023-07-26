<script lang="ts" context="module">
  import Tabs, { type Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: routeConfig.pay.activity.root, label: "Transactions", exact: true },
    { url: routeConfig.pay.activity.conversions.root, label: "FX", exact: true },
  ];
</script>

<script lang="ts">
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import FilterIcon from "components/icons/filter-icon.svelte";
  import { slide } from "svelte/transition";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { transactionStatus } from "models/transaction";
  import { formatTransactionStatus } from "formatting/transaction";
  import * as transactionFilters from "./(transactions)/+page.svelte";
  import * as conversionFilters from "./fx/+page.svelte";
  import { page } from "$app/stores";
  import { conversionStatus } from "models/conversion";
  import { formatConversionStatus } from "formatting/conversion";
  import SearchField from "components/ui/search-field.svelte";
  import routeConfig from "routeConfig";

  let showFilters = false;

  $: view =
    $page.url.pathname === routeConfig.pay.activity.root
      ? ("transactions" as const)
      : ("conversions" as const);
  $: filters = view === "transactions" ? transactionFilters : conversionFilters;
  $: ({ dateRange, status, searchQuery } = filters);
  $: filtersActive = Boolean($dateRange || $status.length);
  $: currTransactionStatus = transactionFilters.status;
  $: currConversionStatus = conversionFilters.status;
  $: viewBreadCrumbs = {
    transactions: {
      url: routeConfig.pay.activity.root,
      label: "Transactions",
    },
    conversions: {
      url: routeConfig.pay.activity.conversions.root,
      label: "FX",
    },
  }[view];
  $: breadCrumbs = [
    {
      url: routeConfig.pay.activity.root,
      label: "Activity",
    },
    viewBreadCrumbs,
  ];

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

<BreadCrumbs items={breadCrumbs} />

<div class="header">
  <h1 class="typography headline-medium bold">Activity</h1>

  <div class="actions">
    <SearchField bind:value={$searchQuery} />

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
        {#if view === "transactions"}
          <StatusPicker
            statuses={transactionStatus}
            bind:value={$currTransactionStatus}
            format={formatTransactionStatus}
            placeholder="Status"
          />
        {:else}
          <StatusPicker
            statuses={conversionStatus}
            bind:value={$currConversionStatus}
            format={formatConversionStatus}
            placeholder="Status"
          />
        {/if}
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
    background-image: var(--color-gradient-extensions-horizontal);
  }
</style>
