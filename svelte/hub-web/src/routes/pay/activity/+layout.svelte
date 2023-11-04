<script lang="ts" context="module">
  import type { Tab } from "components/ui/tabs.svelte";

  const tabs: Tab[] = [
    { url: routeConfig.routes.pay.routes.activity.root, label: "Transactions", exact: true },
    {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: "FX",
      exact: true,
    },
  ];
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";

  $: view =
    $page.url.pathname === routeConfig.routes.pay.routes.activity.root
      ? ("transactions" as const)
      : ("conversions" as const);
  $: viewBreadCrumbs = {
    transactions: {
      url: routeConfig.routes.pay.routes.activity.root,
      label: "Transactions",
    },
    conversions: {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: "FX",
    },
  }[view];
  $: breadCrumbs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: "Activity",
    },
    viewBreadCrumbs,
  ];
</script>

<StandardLayout {breadCrumbs} pageTitle="Activity" {tabs}>
  <slot />
</StandardLayout>
