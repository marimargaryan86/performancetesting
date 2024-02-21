<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";

  const t = getTranslator();
</script>

<BookingLayout
  pageTitle={$t("pages.tripManagement.pages.book.pages.car.pages.select.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.car.pages.select.subTitle")}
>
  <div>TODO: Select car offer</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.root}>Previous</a>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.payment.root}>Next</a>
</BookingLayout>
