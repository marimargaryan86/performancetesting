<script lang="ts" context="module">
  import type { Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: routeConfig.pay.activity.root, label: "Transactions", exact: true },
    { url: routeConfig.pay.activity.conversions.root, label: "FX", exact: true },
  ];
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { transactionStatus } from "models/transaction";
  import { formatTransactionStatus } from "formatting/transaction";
  import * as transactionFilters from "./(transactions)/+page.svelte";
  import * as conversionFilters from "./fx/+page.svelte";
  import { page } from "$app/stores";
  import { conversionStatus } from "models/conversion";
  import { formatConversionStatus } from "formatting/conversion";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";

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
  </svelte:fragment>

  <slot />
</StandardLayout>
