<script lang="ts">
  import type { BreadCrumb } from "components/page/bread-crumbs.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import type { Tab } from "components/ui/tabs.svelte";
  import { getLocaleData } from "i18n";
  import routeConfig from "routeConfig";

  export let data;

  const i18n = getLocaleData();

  let breadCrumbs: BreadCrumb[];
  let tabs: Tab[];

  $: i18nOrders = $i18n.pages.tripManagement.pages.orders;
  $: selfLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
  $: breadCrumbs = [
    {
      label: i18nOrders.title,
      url: routeConfig.routes.tripManagement.routes.orders.root,
    },
    { label: data.order.journey?.reference ?? $i18n.words.unknown, url: selfLink.root },
  ];
  $: tabs = [
    { label: i18nOrders.pages.bookings.title, url: selfLink.root, exact: true },
    { label: i18nOrders.pages.details.title, url: selfLink.routes.details.root },
  ];
</script>

<StandardLayout {breadCrumbs} {tabs}>
  <svelte:fragment slot="page-title">
    {$i18n.words.orderReference}:
    <span class="typography title-large bold">
      {data.order.journey?.reference ?? $i18n.words.unknown}
    </span>
  </svelte:fragment>

  <slot />
</StandardLayout>
