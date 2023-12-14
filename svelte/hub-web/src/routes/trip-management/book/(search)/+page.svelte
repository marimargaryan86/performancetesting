<script lang="ts">
  import { getPageTitle } from "utils/page-title";
  import TripSearch from "../../components/trip-search/trip-search.svelte";
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Trip Management", "Book", "Search")}</title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
