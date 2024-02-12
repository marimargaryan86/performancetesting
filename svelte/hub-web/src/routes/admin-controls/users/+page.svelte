<script lang="ts">
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import routeConfig from "$lib/route-config";
  import { getPageTitle } from "$lib/utils/page-title";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getTranslator } from "$lib/i18n";
  import { getUser, permitted } from "$lib/utils/permissions";

  const t = getTranslator();
  const user = getUser();
</script>

<svelte:head>
  <title>
    {getPageTitle($t("pages.adminControls.pages.users.title"))}
  </title>
</svelte:head>

{#if permitted($user, "users.add")}
  <StandardLayout pageTitle={$t("pages.adminControls.pages.users.title")}>
    <div slot="actions">
      <a
        variant="primary"
        size="small"
        href={routeConfig.routes.adminControls.routes.users.routes.create.root}
      >
        <Icon variant="plus" size="20px" />
        {$t("actions.addUser")}
      </a>
    </div>
  </StandardLayout>
{/if}

<style>
  a:not([variant]) {
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
