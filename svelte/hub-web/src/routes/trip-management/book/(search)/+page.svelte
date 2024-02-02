<script lang="ts">
  import { getPageTitle } from "utils/page-title";
  import TripSearch from "../../components/trip-search/trip-search.svelte";
  import { getLocaleData } from "i18n";
  import type { ComponentEvents } from "svelte";
  import { manager } from "../../booking-flow";
  import { goto } from "$app/navigation";
  import routeConfig from "routeConfig";

  const i18n = getLocaleData();

  async function search(event: ComponentEvents<TripSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    await manager.search(event.detail.data);
    await goto(routeConfig.routes.tripManagement.routes.book.routes.select.root);
    event.detail.pending.set(false);
  }
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
  <TripSearch on:search={search} />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
