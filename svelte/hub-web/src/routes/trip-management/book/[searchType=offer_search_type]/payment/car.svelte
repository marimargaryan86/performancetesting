<script lang="ts">
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import type { PageData } from "./$types";

  const t = getTranslator();

  export let data: PageData;
</script>

<BookingLayout
  pageTitle={$t("pages.tripManagement.pages.book.pages.car.pages.payment.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.car.pages.payment.subTitle")}
>
  <div>TODO: {data.searchType} Payment</div>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.select.root}>Previous</a>
  <a href={routeConfig.routes.tripManagement.routes.book.routes.car.routes.confirmation.root}>
    Next
  </a>
</BookingLayout>
