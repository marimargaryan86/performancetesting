<script lang="ts" context="module">
  export const LIST_ACCOUNTS_LIMIT = 20;
</script>

<script lang="ts">
  import { dev } from "$app/environment";
  import ChevronIcon from "~/components/icons/chevron-icon.svelte";
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import EntityAvatar from "~/components/ui/entity-avatar.svelte";
  import { scrollLoad, type ScrollLoadFunc } from "~/directives/scroll-load";
  import { getLocaleData } from "~/i18n";
  import integrationInstancesClient from "~/integration-instances-client";
  import routeConfig from "~/route-config";
  import { getPageTitle } from "~/utils/page-title";

  export let data;

  const i18n = getLocaleData();

  let searchQuery = "";

  $: accounts = data.accounts.data.filter((account) =>
    account.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.accounts.cursor) {
      return { depleted: true };
    }

    const nextAccounts = await integrationInstancesClient.hub.accounts.find({
      cursor: data.accounts.cursor,
      limit: LIST_ACCOUNTS_LIMIT,
    });

    data.accounts = {
      data: [...data.accounts.data, ...nextAccounts.data],
      cursor: nextAccounts.cursor,
    };

    return { depleted: !nextAccounts.cursor };
  };
</script>

<svelte:head>
  <title>
    {getPageTitle($i18n.title, $i18n.pages.pay.title, $i18n.pages.pay.pages.accounts.title)}
  </title>
</svelte:head>

{#if !dev}
  <div />
{:else}
  <StandardLayout pageTitle={$i18n.pages.pay.pages.accounts.title} bind:searchQuery>
    <div class="wrapper">
      <h2 typography="title-medium" weight="bold">
        {$i18n.words.subAccounts}
      </h2>

      <ul class="accounts" data-sveltekit-preload-data="off" use:scrollLoad={{ func: loadMore }}>
        {#each accounts as account (account.id)}
          <li>
            <a
              href={routeConfig.routes.pay.routes.accounts.routes.account(account.id).root}
              class="account"
            >
              <EntityAvatar name={account.name} size="72px" />
              <span class="account-name" typography="body-large">{account.name}</span>
              <ChevronIcon size="20px" color="var(--color-main-neutral-700)" />
            </a>
          </li>
        {/each}
      </ul>
    </div>
  </StandardLayout>
{/if}

<style>
  .wrapper {
    display: flex;
    flex-flow: column;
    gap: 32px;
    height: 100%;
    padding: 32px 40px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .accounts {
    display: flex;
    flex-flow: column;
    gap: 8px;
    overflow: auto;
  }

  .account-name {
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .account {
    display: flex;
    gap: 32px;
    align-items: center;
    padding: 12px 16px;
    color: var(--color-main-neutral-800);
    text-decoration: none;
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 8px;
  }

  .account :global(.entity-avatar) {
    box-shadow: var(--shadow-3);
  }

  .account :global(.entity-avatar),
  .account :global(.chevron-icon) {
    flex-shrink: 0;
  }
</style>
