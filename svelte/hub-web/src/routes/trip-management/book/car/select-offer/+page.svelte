<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import routeConfig from "$lib/route-config";
</script>

<BookingLayout pageTitle="Select" pageSubTitle="Select Car">
  <div>TODO: Select car offer</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.root}>Previous</a>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.payment.root}>Next</a>
</BookingLayout>
