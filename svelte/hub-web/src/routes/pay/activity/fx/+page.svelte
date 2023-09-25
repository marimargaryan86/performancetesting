<script lang="ts" context="module">
  import type { DateRange } from "models/date-time";
  import { writable } from "svelte/store";

  export const dateRange = writable<DateRange | undefined>(undefined);
  export const status = writable<ConversionStatus[]>([]);
  export const searchQuery = writable("");
</script>

<script lang="ts">
  import { filterConversions } from "filters/conversion";
  import { yymmdd } from "formatting/date-time";
  import type { DirectionY } from "models/spatial";
  import { sortConversions } from "sorting/conversion";
  import { callAction, type FlattenedObject } from "utils/common";
  import Table from "components/ui/table/table.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import { onMount } from "svelte";
  import routeConfig from "routeConfig";
  import type {
    ConversionModel,
    ConversionStatus,
  } from "integration/junction-pay/schemas/conversion";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";

  export let form;
  export let data;

  let sortDirection: DirectionY = "down";
  let sortGroup: FlattenedObject<ConversionModel> = "createdAt";

  $: conversions = sortConversions(
    filterConversions(data.conversions.data, {
      query: $searchQuery,
      dateRange: $dateRange,
      status: $status,
    }),
    { by: sortGroup, direction: sortDirection },
  );

  async function loadMore(): Promise<void> {
    if (!data.conversions.cursor) {
      return;
    }

    await callAction({
      action: routeConfig.routes.pay.routes.activity.routes.conversions.actions.listConversions,
      data: {
        cursor: data.conversions.cursor,
      },
    });

    if (form?.conversions) {
      data.conversions = {
        cursor: form.conversions.cursor,
        data: [...data.conversions.data, ...form.conversions.data],
      };
    }
  }

  onMount(() => {
    $searchQuery = "";
    $dateRange = undefined;
    $status = [];
  });
</script>

<svelte:head>
  <title>FX · Activity · Pay · Junction Hub</title>
</svelte:head>

<Table class="fx-table" {loadMore}>
  <THead>
    <Header>ID</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="createdAt">Created</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="settledAt">Settlement</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="sellAmount.currency">From</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="buyAmount.currency">To</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="transaction.rates.fxQuote">
      Quote Rate
    </Header>
    <Header bind:sortGroup bind:sortDirection sortValue="executedRate">Transaction Rate</Header>
    <Header>FX Delta</Header>
    <Header>FX Buffer</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="fxStatus">Status</Header>
  </THead>

  <TBody>
    {#each conversions as conversion (conversion.id)}
      <TRow>
        <TCol maxWidth="96px" copyable>{conversion.transaction?.bookingId ?? ""}</TCol>
        <TCol class="currency typography bold"
          >{conversion.createdAt ? yymmdd(conversion.createdAt) : ""}</TCol
        >
        <TCol class="currency typography bold"
          >{conversion.settledAt ? yymmdd(conversion.settledAt) : ""}</TCol
        >
        <TCol class="currency typography bold"
          >{conversion.sellAmount?.currency ? conversion.sellAmount.currency : ""}</TCol
        >
        <TCol class="currency typography bold"
          >{conversion.buyAmount?.currency ? conversion.buyAmount.currency : ""}</TCol
        >
        <TCol>{conversion.transaction?.rates.fxQuote ?? ""}</TCol>
        <TCol>{conversion.executedRate}</TCol>
        <TCol>{conversion.fxDelta ?? ""}</TCol>
        <TCol>{conversion.transaction?.rates.fxBuffer ?? ""}</TCol>
        <TStatusBadgeCol value={conversion.fxStatus ?? "unspecified"} />
      </TRow>
    {/each}
  </TBody>
</Table>

<style>
  :global(.table.fx-table) {
    width: 100%;
    height: 100%;
  }

  :global(.table.fx-table .currency) {
    color: var(--color-main-neutral-600);
  }

  :global(.table.fx-table .status-badge) {
    width: 100%;
  }
</style>
