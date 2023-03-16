<script lang="ts">
  import { transactionStatus } from "models/transaction";
  import { page } from "$app/stores";
  import SearchIcon from "components/icons/search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { LayoutData } from "./$types";
  import { formatTransactionStatus } from "formatting/transaction";

  export let data: LayoutData;

  const tabs = [
    { url: "/pay/activity", label: "Transactions" },
    { url: "/pay/activity/fx", label: "FX" },
  ];

  const { searchQuery, dateRange, status } = data;
</script>

<div class="activity layout main-content">
  <h1 class="layout page-header">Activity</h1>

  <div class="layout content-box">
    <ul class="layout tabs">
      {#each tabs as tab}
        <li>
          <a href={tab.url} class="layout tab" class:active={$page.url.pathname === tab.url}>
            {tab.label}
          </a>
        </li>
      {/each}
    </ul>

    <div class="filters">
      <TextField placeholder="Search" bind:value={$searchQuery}>
        <SearchIcon slot="icon-before" color="var(--color-neutral-400)" />
      </TextField>

      <DatePicker range placeholder="Date range" bind:value={$dateRange} />

      <StatusPicker
        placeholder="Status"
        statuses={transactionStatus}
        bind:value={$status}
        format={formatTransactionStatus}
      />
    </div>

    <div class="content">
      <slot />
    </div>
  </div>
</div>

<style>
  .content-box {
    display: flex;
    flex-flow: column;
    gap: 16px;
    height: calc(100% - 48px);
  }

  .filters {
    display: flex;
    gap: 8px;
  }

  .filters > :global(.text-field),
  .filters > :global(.date-picker),
  .filters > :global(.status-picker) {
    --height: 40px;
    --font-size: 12px;
  }

  .filters > :global(.text-field) {
    width: 100%;
    max-width: 240px;
  }

  .content {
    height: calc(100vh - 224px);
    margin: 0 -16px -16px;
    padding: 0 8px;
    overflow: auto;
    background-color: var(--color-generic-white);
    border-radius: 0 0 8px 8px;
  }
</style>
