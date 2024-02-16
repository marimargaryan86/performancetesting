<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import routeConfig from "$lib/route-config";
</script>

<BookingLayout pageTitle="Confirmation" pageSubTitle="Confirmation">
  <div>TODO: Car Confirmation</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.root}>New search</a>
</BookingLayout>
