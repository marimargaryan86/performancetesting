<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatAmount } from "formatting/currency";
  import type { MoneyModel } from "models/money";
  import type { PageData } from "./$types";
  import AddBalanceDialogue from "./add-balance-dialogue.svelte";

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
  exclude={balances}
  accountId={data.account.id}
  token={data.token}
  on:addbalances={addBalances}
  bind:this={dialogue}
/>

<div class="header">
  <TextField placeholder="Find a balance" bind:value={searchQuery}>
    <SearchIcon slot="icon-before" color="var(--color-neutral-400)" />
  </TextField>

  <button class="add-balance" on:click={openDialogue}>
    <PlusIcon color="var(--color-neutral-50)" />
    <span>Add</span>
  </button>
</div>

<ul class="balances">
  {#each balances as balance}
    <li class="balance">
      <a href="/pay/accounts/{data.account.id}/{balance.currency.toLowerCase()}">
        <CurrencyFlag code={balance.currency} />

        <span>
          <strong>{formatAmount(balance)}</strong>
          <span>{balance.currency}</span>
        </span>

        <ChevronIcon color="var(--color-neutral-700)" size="20px" />
      </a>
    </li>
  {:else}
    <li class="empty">No balances found</li>
  {/each}
</ul>

<style>
  .header {
    display: flex;
    gap: 16px;
    justify-content: space-between;
  }

  .header > :global(.text-field) {
    --height: 40px;
    --font-size: 12px;

    width: 400px;
  }

  @media screen and (max-width: 1439px) {
    .header > :global(.text-field) {
      max-width: 255px;
    }
  }

  .add-balance {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 0 40px;
    color: var(--color-neutral-50);
    font-weight: 500;
    font-size: 16px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 24px;
    text-decoration: none;
    background-image: var(--color-positive-gradient);
    border: 0;
    border-radius: 8px;
    cursor: pointer;
  }

  .balances {
    display: flex;
    flex-flow: column;
    gap: 8px;
    height: calc(100vh - 228px);
    margin: 24px -24px -24px;
    padding: 0 24px 24px;
    overflow-y: auto;
  }

  .balance > a {
    display: flex;
    gap: 24px;
    align-items: center;
    height: 60px;
    padding: 0 16px;
    color: var(--color-neutral-800);
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 24px;
    text-decoration: none;
    background-color: var(--color-generic-white);
    border: var(--color-neutral-200) 1px solid;
    border-radius: 8px;
  }

  .balance > a > span {
    display: flex;
    flex-grow: 1;
    gap: 8px;
    align-items: center;
  }

  .balance > a > :global(.currency-flag),
  .balance > a > :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .balance > a > span > strong {
    font-weight: 700;
    font-size: 20px;
  }

  .balance > a > span > span {
    font-weight: 500;
    font-size: 10px;
    letter-spacing: 2px;
  }

  .empty {
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
  }
</style>
