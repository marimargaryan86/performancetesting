<script lang="ts" context="module">
  const tabs: (Tab & { icon?: ComponentType })[] = [
    {
      url: routeConfig.routes.help.routes.privacyPolicy.root,
      label: "Privacy Policy",
      exact: true,
    },
    {
      url: routeConfig.routes.help.routes.termsAndConditions.root,
      label: "Terms and Conditions",
      exact: true,
    },
    {
      icon: HeadphonesIcon,
      url: routeConfig.routes.help.routes.customerService.root,
      label: "Customer Service",
      exact: true,
    },
  ];

  const routes: string[] = [
    routeConfig.routes.help.routes.privacyPolicy.root,
    routeConfig.routes.help.routes.termsAndConditions.root,
    routeConfig.routes.help.routes.customerService.root,
  ];
</script>

<script lang="ts">
  import type { Tab } from "components/ui/tabs.svelte";
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import StandardLayout from "components/page/standard-layout.svelte";
  import { page } from "$app/stores";
  import type { ComponentType } from "svelte";
  import HeadphonesIcon from "components/icons/headphones-icon.svelte";

  $: ({ prevHref, nextHref } = getHrefs($page.url.pathname));
  $: activeTab = tabs.find((item) => {
    return item.exact ? $page.url.pathname === item.url : $page.url.pathname.startsWith(item.url);
  });

  function getHrefs(pathname: string): { prevHref?: string; nextHref?: string } {
    return {
      prevHref: routes[routes.indexOf(pathname) - 1],
      nextHref: routes[routes.indexOf(pathname) + 1],
    };
  }
</script>

<svelte:head>
  <title>{activeTab?.label ?? "Unknown"} · Help · Junction Hub</title>
</svelte:head>

<StandardLayout pageTitle="Help" {tabs} searchQuery="">
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

  <Button
    href={prevHref}
    disabled={!prevHref}
    size="small"
    variant="text"
    slot="navigation-left"
    minWidth="140px"
  >
    Go Back
  </Button>

  <Button
    href={nextHref}
    disabled={!nextHref}
    size="small"
    slot="navigation-right"
    minWidth="140px"
  >
    Next
  </Button>
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
