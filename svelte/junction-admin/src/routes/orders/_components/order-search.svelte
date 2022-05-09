<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import SelectInput from "$lib/components/ui/select-input.svelte";
  import TextInput from "$lib/components/ui/text-input.svelte";
  import SearchIcon from "$lib/icons/search-icon.svelte";
  import type { OrderSearchData, OrderStatus } from "$lib/models/order";
  import ContextMenu from "$lib/partials/context-menu.svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher<{ search: OrderSearchData }>();

  export let spnr: string = "";
  export let reseller: string = "";
  export let status: OrderStatus = undefined;

  const orderStatuses: OrderStatus[] = ["awaiting-payment", "completed", "pending"];

  function search(): void {
    dispatch("search", { spnr, reseller, status });
  }
</script>

<ContextMenu>
  <form on:submit|preventDefault={search} class="search">
    <TextInput label="SPNR" bind:value={spnr} />

    <TextInput label="Reseller" bind:value={reseller} />

    <SelectInput label="Status" items={orderStatuses} bind:value={status} />

    <Button submit>
      <SearchIcon />
      <span>Search</span>
    </Button>
  </form>
</ContextMenu>

<style>
  .search {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
  }
</style>
