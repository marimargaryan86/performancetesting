<script lang="ts">
  import SortButton from "components/ui/sort-button.svelte";
  import { filterConversions } from "filters/conversion";
  import { yymmdd } from "formatting/date-time";
  import type { ConversionModel } from "models/conversion";
  import type { DirectionY } from "models/spatial";
  import { sortConversions } from "sorting/conversion";
  import type { FlattenedObject } from "utils/common";
  import type { PageData } from "./$types";

  export let data: PageData;

  const { searchQuery, dateRange } = data;

  let sortDirection: DirectionY = "down";
  let sortBy: FlattenedObject<ConversionModel> = "id";

  $: conversions = sortConversions(
    filterConversions(data.conversions, {
      query: $searchQuery,
      dateRange: $dateRange,
    }),
    { by: sortBy, direction: sortDirection },
  );
</script>

<svelte:head>
  <title>FX · Activity · Pay · Junction Hub</title>
</svelte:head>

<table class="table-1">
  <thead>
    <th>
      <SortButton
        value="transaction.reference"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="ID"
      />
    </th>
    <th>
      <SortButton
        value="executedAt"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Executed"
      />
    </th>
    <th>
      <SortButton
        value="settledAt"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Settlement"
      />
    </th><th>
      <SortButton
        value="sellAmount.currency"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="From"
      />
    </th>
    <th>
      <SortButton
        value="buyAmount.currency"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="To"
      />
    </th>
    <th>
      <SortButton
        value="transaction.rates.fxQuote"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Quote Rate"
      />
    </th>
    <th>
      <SortButton
        value="executedRate"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Transaction Rate"
      />
    </th>
    <th>
      <SortButton
        value="fxDelta"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="FX Delta"
      />
    </th>
    <th>
      <SortButton
        value="transaction.rates.fxBuffer"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="FX Buffer"
      />
    </th>
    <th>
      <SortButton
        value="fxStatus"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Status"
      />
    </th>
  </thead>

  <tbody>
    {#each conversions as conversion}
      <tr>
        <td>{conversion.transaction?.reference ?? ""}</td>
        <td>{yymmdd(conversion.executedAt)}</td>
        <td>{yymmdd(conversion.settledAt)}</td>
        <td>{conversion.sellAmount.currency}</td>
        <td>{conversion.buyAmount.currency}</td>
        <td>{conversion.transaction?.rates.fxQuote ?? ""}</td>
        <td>{conversion.executedRate}</td>
        <td>{conversion.fxDelta ?? ""}</td>
        <td>{conversion.transaction?.rates.fxBuffer ?? ""}</td>
        <td>{conversion.fxStatus}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .table-1 {
    width: 100%;
  }
</style>
