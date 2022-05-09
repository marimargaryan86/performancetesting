<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import CoordinatesInput from "$lib/components/ui/coordinates-input.svelte";
  import RangeInput from "$lib/components/ui/range-input.svelte";
  import TextInput from "$lib/components/ui/text-input.svelte";
  import SearchIcon from "$lib/icons/search-icon.svelte";
  import type { PlaceSearchData } from "$lib/models/place";
  import ContextMenu from "$lib/partials/context-menu.svelte";
  import { createEventDispatcher } from "svelte";

  export let name = "";
  export let proximity = 0;
  export let latitude: number = undefined;
  export let longitude: number = undefined;

  $: coordinates = { latitude, longitude };

  const dispatch = createEventDispatcher<{ search: PlaceSearchData }>();

  function search(): void {
    dispatch("search", { name, proximity, coordinates });
  }
</script>

<ContextMenu>
  <form on:submit|preventDefault={search} class="search">
    <TextInput label="Name" bind:value={name} />

    <CoordinatesInput bind:latitude bind:longitude />

    <RangeInput
      label="Proximity"
      formatter={(value) => `${value} m`}
      bind:value={proximity}
      min={0}
      max={1000}
    />

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
