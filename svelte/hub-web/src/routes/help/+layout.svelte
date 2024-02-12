<script lang="ts">
  import type { Tab } from "$lib/components/ui/tabs.svelte";
  import routeConfig from "$lib/route-config";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import { page } from "$app/stores";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getTranslator } from "$lib/i18n";

  const t = getTranslator();

  let tabs: (Tab & { icon?: string })[];

  $: tabs = [
    {
      url: routeConfig.routes.help.routes.privacyPolicy.root,
      label: $t("pages.help.pages.privacyPolicy.title"),
      exact: true,
    },
    {
      url: routeConfig.routes.help.routes.termsAndConditions.root,
      label: $t("pages.help.pages.termsAndConditions.title"),
      exact: true,
    },
    {
      icon: "headphones",
      url: routeConfig.routes.help.routes.customerService.root,
      label: $t("pages.help.pages.customerService.title"),
      exact: true,
    },
    {
      url: routeConfig.routes.help.routes.conditionsOfCarriage.root,
      label: $t("pages.help.pages.conditionsOfCarriage.title"),
      exact: true,
    },
  ];
  $: activeTab = tabs.find((item) => {
    return item.exact ? $page.url.pathname === item.url : $page.url.pathname.startsWith(item.url);
  });
</script>

<svelte:head>
  <title>
    {getPageTitle($t("title"), $t("pages.help.title"), activeTab?.label ?? $t("words.unknown"))}
  </title>
</svelte:head>

<StandardLayout pageTitle={$t("pages.help.title")} {tabs} searchQuery="">
  {#key $page.url.pathname}
    <div class="container">
      {#if activeTab?.icon}
        <img src="/images/icons/{activeTab.icon}.svg" alt="" />
      {/if}

      <h1 typography="title-medium" weight="bold">
        {activeTab?.label ?? undefined}
      </h1>

      <div typography="body-medium" class="content">
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

  img {
    width: 60px;
    height: 60px;
  }

  .content {
    color: var(--color-common-light-soft);
  }
</style>
