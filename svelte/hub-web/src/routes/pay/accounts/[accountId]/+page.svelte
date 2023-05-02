<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import { formatAmount } from "formatting/currency";
  import type { MoneyModel } from "models/money";
  import type { PageData } from "./$types";
  import AddBalanceDialogue from "./add-balance-dialogue.svelte";
  import SearchField from "components/ui/search-field.svelte";
  import Button from "components/ui/button.svelte";

  export let data: PageData;

  let searchQuery = "";
  let dialogue: AddBalanceDialogue;

  $: balances = data.balances
    .filter((item) => item.currency.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => 0 - (a.currency < b.currency ? 1 : -1));

  function openDialogue(): void {
    dialogue.open();
  }

  function addBalances(event: CustomEvent<MoneyModel[]>): void {
    data.balances = [...event.detail, ...data.balances];
  }
</script>

<svelte:head>
  <title>Balances · {data.account.name} · Accounts · Pay · Junction Hub</title>
</svelte:head>

<AddBalanceDialogue
  currencies={data.currencies}
  exclude={balances}
  accountId={data.account.id}
  token={data.token}
  on:addbalances={addBalances}
  bind:this={dialogue}
/>

<div class="header">
  <h1 class="typography headline-medium bold">Balances</h1>

  <div class="actions">
    <SearchField bind:value={searchQuery} />

    <Button size="small" on:click={openDialogue}>
      Add Balance
      <PlusIcon />
    </Button>
  </div>
</div>

<div class="content">
  <ul class="balances">
    {#each balances as balance}
      <li>
        <a href="#top" class="balance">
          <CurrencyFlag code={balance.currency} />

          <span>
            <strong class="typography body-large bold">
              {formatAmount(balance, data.currencies)}
            </strong>
            <span class="typography body-small">{balance.currency}</span>
          </span>

          <ChevronIcon color="var(--color-main-neutral-700)" size="20px" />
        </a>
      </li>
    {:else}
      <li class="typography body-large empty">No balances found</li>
    {/each}
  </ul>
</div>

<style>
  .header {
    display: flex;
    justify-content: space-between;
    padding: 8px 24px 24px;
  }

  .actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }

  .balances {
    display: flex;
    flex-flow: column;
    gap: 8px;
    height: 100%;
    padding: 32px 40px;
    overflow-y: auto;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .balance {
    display: flex;
    gap: 24px;
    align-items: center;
    height: 60px;
    padding: 16px;
    text-decoration: none;
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 8px;
  }

  .balance > span {
    display: flex;
    flex-grow: 1;
    gap: 8px;
    align-items: center;
    color: var(--color-main-neutral-800);
  }

  .balance > :global(.currency-flag),
  .balance > :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .empty {
    color: var(--color-main-neutral-600);
  }
</style>
