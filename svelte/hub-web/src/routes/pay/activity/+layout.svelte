<script lang="ts">
  import type { Tab } from "components/ui/tabs.svelte";
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";
  import { getLocaleData } from "i18n";
  import { ensureDefined } from "utils/array";

  const i18n = getLocaleData();

  let tabs: Tab[];

  $: tabs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $i18n.pages.pay.pages.activity.pages.transactions.title,
      exact: true,
    },
    {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: $i18n.pages.pay.pages.activity.pages.conversions.title,
      exact: true,
    },
  ];
  $: breadCrumbs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $i18n.pages.pay.pages.activity.title,
    },
    tabs.find((item) => item.url === $page.url.pathname),
  ].filter(ensureDefined);
</script>

<StandardLayout {breadCrumbs} pageTitle={$i18n.pages.pay.pages.activity.title} {tabs}>
  <slot />
</StandardLayout>
