<script lang="ts">
  import type { Tab } from "~/components/ui/tabs.svelte";
  import { page } from "$app/stores";
  import routeConfig from "~/route-config";
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import { getTranslator } from "~/i18n";
  import { ensureDefined } from "~/utils/array";

  const t = getTranslator();

  let tabs: Tab[];

  $: tabs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $t("pages.pay.pages.activity.pages.transactions.title"),
      exact: true,
    },
    {
      url: routeConfig.routes.pay.routes.activity.routes.conversions.root,
      label: $t("pages.pay.pages.activity.pages.conversions.title"),
      exact: true,
    },
  ];
  $: breadCrumbs = [
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $t("pages.pay.pages.activity.title"),
    },
    tabs.find((item) => item.url === $page.url.pathname),
  ].filter(ensureDefined);
</script>

<StandardLayout {breadCrumbs} pageTitle={$t("pages.pay.pages.activity.title")} {tabs}>
  <slot />
</StandardLayout>
