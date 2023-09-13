<script lang="ts">
  import { goto } from "$app/navigation";
  import { pendableCall } from "utils/pendable-call";
  import TripSearch from "../trip-search/trip-search.svelte";

  const { pending, func: search } = pendableCall((event: CustomEvent<URL>) => goto(event.detail));
</script>

<svelte:head>
  <title>Search · Book · Trip Management · Junction Hub</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch on:search={search} pending={$pending} />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
