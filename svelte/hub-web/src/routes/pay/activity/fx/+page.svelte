<script lang="ts">
  import { filterConversions } from "filters/conversion";
  import { yymmdd } from "formatting/date-time";
  import type { ConversionModel } from "models/conversion";
  import type { DirectionY } from "models/spatial";
  import { sortConversions } from "sorting/conversion";
  import type { FlattenedObject } from "utils/common";
  import type { PageData } from "./$types";
  import Table from "components/ui/table/table.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import ConversionStatusBadge from "components/ui/conversion-status-badge.svelte";

  export let data: PageData;

  const { searchQuery, dateRange } = data;

  let sortDirection: DirectionY = "down";
  let sortGroup: FlattenedObject<ConversionModel> = "id";

  $: conversions = sortConversions(
    filterConversions(data.conversions, {
      query: $searchQuery,
      dateRange: $dateRange,
    }),
    { by: sortGroup, direction: sortDirection },
  );
</script>

<svelte:head>
  <title>FX · Activity · Pay · Junction Hub</title>
</svelte:head>

<Table class="fx-table">
  <THead>
    <Header>Parent ID</Header>
    <Header>ID</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="executedAt">Executed</Header>
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
    {#each conversions as conversion}
      <TRow>
        <TCol maxWidth="96px">{conversion.transaction?.reference ?? ""}</TCol>
        <TCol maxWidth="96px">{conversion.id}</TCol>
        <TCol>{yymmdd(conversion.executedAt)}</TCol>
        <TCol>{yymmdd(conversion.settledAt)}</TCol>
        <TCol class="currency typography bold">{conversion.sellAmount.currency}</TCol>
        <TCol class="currency typography bold">{conversion.buyAmount.currency}</TCol>
        <TCol>{conversion.transaction?.rates.fxQuote ?? ""}</TCol>
        <TCol>{conversion.executedRate}</TCol>
        <TCol>{conversion.fxDelta ?? ""}</TCol>
        <TCol>{conversion.transaction?.rates.fxBuffer ?? ""}</TCol>
        <TCol width="124px"><ConversionStatusBadge value={conversion.fxStatus} /></TCol>
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
