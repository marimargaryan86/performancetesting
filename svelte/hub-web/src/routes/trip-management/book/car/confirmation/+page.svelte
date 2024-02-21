<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";

  const t = getTranslator();
</script>

<BookingLayout
  pageTitle={$t("pages.tripManagement.pages.book.pages.car.pages.confirmation.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.car.pages.confirmation.subTitle")}
>
  <div>TODO: Car Confirmation</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.root}>New search</a>
</BookingLayout>
