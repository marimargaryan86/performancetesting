<script lang="ts">
  import { goto } from "$app/navigation";
  import { manager } from "$lib/components/pages/trip-management/booking-flow-car/booking-flow";
  import CarSearch from "$lib/components/pages/trip-management/booking-flow-car/search/car-search.svelte";
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import routeConfig from "$lib/route-config";
  import type { ComponentEvents } from "svelte";

  async function search(event: ComponentEvents<CarSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    try {
      await manager.search(event.detail.data);
      await goto(routeConfig.routes.tripManagement.routes.book.routes.car.routes.select.root);
    } finally {
      event.detail.pending.set(false);
    }
  }
</script>

<BookingLayout pageTitle="Search" pageSubTitle="Search for Car Rental">
  <div class="search-wrapper">
    <CarSearch on:search={search} />
  </div>
</BookingLayout>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
