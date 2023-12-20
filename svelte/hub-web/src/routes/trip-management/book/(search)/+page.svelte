<script lang="ts">
  import { getPageTitle } from "utils/page-title";
  import TripSearch from "../../components/trip-search/trip-search.svelte";
  import { getLocaleData } from "i18n";

  const i18n = getLocaleData();
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.book.title,
      $i18n.pages.tripManagement.pages.book.pages.search.title,
    )}
  </title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
