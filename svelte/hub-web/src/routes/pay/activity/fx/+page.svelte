<script lang="ts">
  import SortButton from "components/ui/sort-button.svelte";
  import { yymmdd } from "formatting/date-time";
  import type { ConversionModel } from "models/conversion";
  import type { DirectionY } from "models/spatial";
  import type { FlattenedObject } from "utils/common";
  import type { PageData } from "./$types";

  export let data: PageData;

  let sortDirection: DirectionY = "down";
  let sortBy: FlattenedObject<ConversionModel> = "id";
</script>

<svelte:head>
  <title>FX · Activity · Pay · Junction Hub</title>
</svelte:head>

<table class="table-1">
  <thead>
    <th><SortButton value="id" bind:direction={sortDirection} bind:group={sortBy} label="ID" /></th>
    <th>
      <SortButton value="rate" bind:direction={sortDirection} bind:group={sortBy} label="Rate" />
    </th>
    <th>
      <SortButton
        value="settledAt"
        bind:direction={sortDirection}
        bind:group={sortBy}
        label="Settlement Date"
      />
    </th>
  </thead>

  <tbody>
    {#each data.conversions as conversion}
      <tr>
        <td>{conversion.id}</td>
        <td>{conversion.rate}</td>
        <td>{yymmdd(conversion.settledAt)}</td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .table-1 {
    width: 100%;
  }
</style>
