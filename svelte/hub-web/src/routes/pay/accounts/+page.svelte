<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import SearchField from "components/ui/search-field.svelte";
  import { scrollLoad } from "directives/scroll-load";
  import routeConfig from "routeConfig";
  import { callAction } from "utils/common";

  export let form;
  export let data;

  let searchQuery = "";

  $: accounts = data.accounts.data.filter((account) =>
    account.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  async function loadMore(): Promise<void> {
    if (!data.accounts.cursor) {
      return;
    }

    await callAction(routeConfig.pay.accounts.actions.listAccounts, {
      cursor: data.accounts.cursor,
    });

    if (form?.accounts) {
      data.accounts = {
        cursor: form.accounts.cursor,
        data: [...data.accounts.data, ...form.accounts.data],
      };
    }
  }
</script>

<svelte:head>
  <title>Accounts · Pay · Junction Hub</title>
</svelte:head>

<div class="header">
  <h1 class="typography headline-medium bold">Accounts</h1>

  <SearchField bind:value={searchQuery} />
</div>

<div class="content">
  <div class="wrapper">
    <h2 class="typography title-medium bold">Sub accounts</h2>

    <ul class="accounts" data-sveltekit-preload-data="off" use:scrollLoad={{ func: loadMore }}>
      {#each accounts as account}
        <li>
          <a href={routeConfig.pay.accounts.account(account.id)} class="account">
            <EntityAvatar name={account.name} size="72px" />
            <span class="account-name typography body-large">{account.name}</span>
            <ChevronIcon size="20px" color="var(--color-main-neutral-700)" />
          </a>
        </li>
      {/each}
    </ul>
  </div>
</div>

<style>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32px 24px;
    color: var(--color-main-neutral-800);
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }

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
