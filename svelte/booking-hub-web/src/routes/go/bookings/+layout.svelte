<script lang="ts" context="module">
  import Tabs, { type Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: routeConfig.go.bookings.root, label: "All", exact: true },
    { url: routeConfig.go.bookings.refunds, label: "Refunds", exact: true },
  ];
</script>

<script lang="ts">
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import FilterIcon from "components/icons/filter-icon.svelte";
  import { slide } from "svelte/transition";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { page } from "$app/stores";
  import { conversionStatus } from "models/conversion";
  import { formatConversionStatus } from "formatting/conversion";
  import SearchField from "components/ui/search-field.svelte";
  import routeConfig from "routeConfig";

  let showFilters = false;

  $: view =
    $page.url.pathname === routeConfig.go.bookings.root ? ("all" as const) : ("refunds" as const);
  $: viewBreadCrumbs = {
    all: {
      url: routeConfig.go.bookings.root,
      label: "All",
    },
    refunds: {
      url: routeConfig.go.bookings.refunds,
      label: "Refunds",
    },
  }[view];
  $: breadCrumbs = [
    {
      url: routeConfig.go.bookings.root,
      label: "Bookings",
    },
    viewBreadCrumbs,
  ];

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

<BreadCrumbs items={breadCrumbs} />

<div class="header">
  <h1 class="typography headline-medium bold">Bookings</h1>

  <div class="actions">
    <SearchField />

    <button on:click={toggleFilters}>
      <FilterIcon color="var(--color-main-primary-500)" />
    </button>
  </div>
</div>

<div class="tabs">
  {#if showFilters}
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
