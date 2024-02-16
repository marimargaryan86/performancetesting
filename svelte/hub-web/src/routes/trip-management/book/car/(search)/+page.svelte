<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import routeConfig from "$lib/route-config";
</script>

<BookingLayout pageTitle="Search" pageSubTitle="Search for Car Rental">
  <div>TODO: Search for car</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.select.root}>Next</a>
</BookingLayout>
