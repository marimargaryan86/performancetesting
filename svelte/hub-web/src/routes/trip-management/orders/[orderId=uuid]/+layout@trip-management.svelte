<script lang="ts">
  import type { BreadCrumb } from "components/page/bread-crumbs.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import type { Tab } from "components/ui/tabs.svelte";
  import routeConfig from "routeConfig";

  export let data;

  let breadCrumbs: BreadCrumb[] = [];
  let tabs: Tab[] = [];

  $: selfLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
  $: breadCrumbs = [
    { label: "Orders", url: routeConfig.routes.tripManagement.routes.orders.root },
    { label: data.order.journey?.reference ?? "Unknown", url: selfLink.root },
  ];
  $: tabs = [
    { label: "Bookings", url: selfLink.root, exact: true },
    { label: "Details", url: selfLink.routes.details.root },
  ];
</script>

<StandardLayout {breadCrumbs} {tabs} searchQuery="">
  <svelte:fragment slot="page-title">
    Order reference:
    <span class="typography title-large bold">
      {data.order.journey?.reference ?? "Unknown"}
    </span>
  </svelte:fragment>

  <slot />
</StandardLayout>
