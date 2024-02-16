<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import routeConfig from "$lib/route-config";
</script>

<BookingLayout pageTitle="Payment" pageSubTitle="Payment">
  <div>TODO: Car Payment</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.select.root}>Previous</a>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.confirmation.root}>
    Next
  </a>
</BookingLayout>
