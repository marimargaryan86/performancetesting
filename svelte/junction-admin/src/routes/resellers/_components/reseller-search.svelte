<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import TextInput from "$lib/components/ui/text-input.svelte";
  import SearchIcon from "$lib/icons/search-icon.svelte";
  import type { ResellerSearchData } from "$lib/models/reseller";
  import ContextMenu from "$lib/partials/context-menu.svelte";
  import { createEventDispatcher } from "svelte";

  let name = "";

  const dispatch = createEventDispatcher<{ search: ResellerSearchData }>();

  function search(): void {
    dispatch("search", { name });
  }
</script>

<ContextMenu>
  <form on:submit|preventDefault={search} class="search">
    <TextInput label="Name" bind:value={name} />

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
