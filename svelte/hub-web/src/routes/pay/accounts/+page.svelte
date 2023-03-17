<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;

  let searchQuery = "";

  $: accounts = data.accounts.filter((account) =>
    account.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );
</script>

<svelte:head>
  <title>Accounts · Pay · Junction Hub</title>
</svelte:head>

<h1 class="layout page-header">Accounts</h1>

<div class="layout content-box">
  <div class="header">
    <TextField placeholder="Find an account" bind:value={searchQuery}>
      <SearchIcon slot="icon-before" color="var(--color-neutral-400)" />
    </TextField>
  </div>

  <ul class="accounts">
    {#each accounts as account}
      <li class:head-account={account.headAccount} class="account">
        <a href="/pay/accounts/{account.id}">
          <EntityAvatar name={account.name} size="72px" />
          <span class="ellipsis">{account.name}</span>
          <ChevronIcon size="20px" color="var(--color-neutral-700)" />
        </a>
      </li>
    {/each}
  </ul>
</div>

<style>
  .layout.content-box {
    padding: 24px;
  }

  .header {
    margin-bottom: 24px;
  }

  .header > :global(.text-field) {
    --height: 40px;
    --font-size: 12px;

    width: 100%;
    max-width: 400px;
  }

  @media screen and (max-width: 1439px) {
    .header > :global(.text-field) {
      max-width: 255px;
    }
  }

  .accounts {
    display: flex;
    flex-flow: column;
    gap: 8px;
    height: calc(100vh - 196px);
    margin: 0 -16px -24px;
    padding: 0 16px 24px;
    overflow: auto;
    font-weight: 600;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 20px;
    letter-spacing: 0.1px;
  }

  .account > a {
    display: flex;
    gap: 32px;
    align-items: center;
    padding: 12px 16px;
    color: var(--color-neutral-800);
    text-decoration: none;
    background-color: var(--color-generic-white);
    border: var(--color-neutral-500) 1px solid;
    border-radius: 8px;
  }

  .account.head-account > a {
    font-weight: 700;
    background-color: var(--color-primary-100);
    border-color: var(--color-primary-500);
  }

  .account.head-account + .account {
    margin-top: 24px;
  }

  .account :global(.entity-avatar),
  .account :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .account > a > span {
    flex-grow: 1;
  }
</style>
