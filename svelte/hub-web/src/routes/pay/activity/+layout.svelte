<script lang="ts" context="module">
  import type { Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: routeConfig.routes.pay.routes.activity.root, label: "Transactions", exact: true },
    {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: "FX",
      exact: true,
    },
  ];
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import * as transactionFilters from "./(transactions)/+page.svelte";
  import * as conversionFilters from "./fx/+page.svelte";
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";
  import { capitalize } from "utils/common";

  $: view =
    $page.url.pathname === routeConfig.routes.pay.routes.activity.root
      ? ("transactions" as const)
      : ("conversions" as const);
  $: filters = view === "transactions" ? transactionFilters : conversionFilters;
  $: ({ dateRange, status, searchQuery } = filters);
  $: filtersActive = Boolean($dateRange || $status.length);
  $: currTransactionStatus = transactionFilters.status;
  $: currConversionStatus = conversionFilters.status;
  $: viewBreadCrumbs = {
    transactions: {
      url: routeConfig.routes.pay.routes.activity.root,
      label: "Transactions",
    },
    conversions: {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: "FX",
    },
  }[view];
  $: breadCrumbs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: "Activity",
    },
    viewBreadCrumbs,
  ];
</script>

<StandardLayout
  {breadCrumbs}
  pageTitle="Activity"
  {tabs}
  {filtersActive}
  bind:searchQuery={$searchQuery}
>
  <svelte:fragment slot="filters">
    <DatePicker bind:value={$dateRange} range placeholder="Date Range" />

    {#if view === "transactions"}
      <StatusPicker
        statuses={["paid", "pending", "cancelled"]}
        bind:value={$currTransactionStatus}
        format={capitalize}
        placeholder="Status"
      />
    {:else}
      <StatusPicker
        statuses={["executed", "unspecified", "failed"]}
        bind:value={$currConversionStatus}
        format={capitalize}
        placeholder="Status"
      />
    {/if}
  </svelte:fragment>

  <slot />
</StandardLayout>
