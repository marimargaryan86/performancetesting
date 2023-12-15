<script lang="ts">
  import type { Tab } from "components/ui/tabs.svelte";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";
  import { page } from "$app/stores";
  import type { ComponentType } from "svelte";
  import HeadphonesIcon from "components/icons/headphones-icon.svelte";
  import { getPageTitle } from "utils/page-title";
  import { getLocaleData } from "i18n";

  const i18n = getLocaleData();

  let tabs: (Tab & { icon?: ComponentType })[];

  $: tabs = [
    {
      url: routeConfig.routes.help.routes.privacyPolicy.root,
      label: $i18n.pages.help.pages.privacyPolicy.title,
      exact: true,
    },
    {
      url: routeConfig.routes.help.routes.termsAndConditions.root,
      label: $i18n.pages.help.pages.termsAndConditions.title,
      exact: true,
    },
    {
      icon: HeadphonesIcon,
      url: routeConfig.routes.help.routes.customerService.root,
      label: $i18n.pages.help.pages.customerService.title,
      exact: true,
    },
    {
      url: routeConfig.routes.help.routes.conditionsOfCarriage.root,
      label: $i18n.pages.help.pages.conditionsOfCarriage.title,
      exact: true,
    },
  ];
  $: activeTab = tabs.find((item) => {
    return item.exact ? $page.url.pathname === item.url : $page.url.pathname.startsWith(item.url);
  });
</script>

<svelte:head>
  <title>
    {getPageTitle($i18n.title, $i18n.pages.help.title, activeTab?.label ?? $i18n.words.unknown)}
  </title>
</svelte:head>

<StandardLayout pageTitle={$i18n.pages.help.title} {tabs} searchQuery="">
  {#key $page.url.pathname}
    <div class="container">
      {#if activeTab?.icon}
        <svelte:component this={activeTab.icon} />
      {/if}

      <h1 class="typography bold title-medium">
        {activeTab?.label ?? undefined}
      </h1>

      <div class="content typography body-medium">
        <slot />
      </div>
    </div>
  {/key}
</StandardLayout>

<style>
  .container {
    display: flex;
    flex-flow: column;
    gap: 24px;
    height: 100%;
    padding: 56px 120px 80px;
    overflow: auto;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h1 {
    color: var(--color-main-primary-900);
  }

  .content {
    color: var(--color-common-light-soft);
  }
</style>
