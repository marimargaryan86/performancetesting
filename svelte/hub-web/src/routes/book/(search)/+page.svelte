<script lang="ts">
  import { goto } from "$app/navigation";
  import TripSearch from "../trip-search/trip-search.svelte";

  function search(event: CustomEvent<URL>): void {
    goto(event.detail);
  }
</script>

<svelte:head>
  <title>Search · Book · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch on:search={search} />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
