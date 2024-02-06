<script lang="ts">
  import type { BreadCrumb } from "~/components/page/bread-crumbs.svelte";
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import type { Tab } from "~/components/ui/tabs.svelte";
  import { getTranslator } from "~/i18n";
  import routeConfig from "~/route-config";

  export let data;

  const t = getTranslator();

  let breadCrumbs: BreadCrumb[];
  let tabs: Tab[];

  $: i18nOrders = $t("pages.tripManagement.pages.orders", { returnObjects: true });
  $: selfLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
  $: breadCrumbs = [
    {
      label: i18nOrders.title,
      url: routeConfig.routes.tripManagement.routes.orders.root,
    },
    { label: data.order.journey?.reference ?? $t("words.unknown"), url: selfLink.root },
  ];
  $: tabs = [
    { label: i18nOrders.pages.bookings.title, url: selfLink.root, exact: true },
    { label: i18nOrders.pages.details.title, url: selfLink.routes.details.root },
  ];
</script>

<StandardLayout {breadCrumbs} {tabs}>
  <svelte:fragment slot="page-title">
    {$t("words.orderReference")}:
    <span typography="title-large" weight="bold">
      {data.order.journey?.reference ?? $t("words.unknown")}
    </span>
  </svelte:fragment>

  <slot />
</StandardLayout>
