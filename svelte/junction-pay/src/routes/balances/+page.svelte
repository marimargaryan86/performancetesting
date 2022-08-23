<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import AddIcon from "$lib/icons/add-icon.svelte";
  import SearchIcon from "$lib/icons/search-icon.svelte";
  import utils from "$lib/utils";
  import type { BalanceModel } from "$models/balance-models";
  import instances from "$services/instances";
  import { onMount } from "svelte";
  import Layout from "./layout.svelte";

  let balances: BalanceModel[] = [];

  const { balance: service } = instances;
  const { func: findBalances } = utils.pendableCall(service.findBalances.bind(service));

  onMount(async () => {
    try {
      balances = await findBalances();
    } catch {
      //
    }
  });
</script>

<svelte:head>
  <title>Junction | Balances</title>
</svelte:head>

<Layout>
  <div class="search" slot="action">
    <SearchIcon />
    <TextField placeholder="Find a balance" />
  </div>

  <div class="balances" slot="body">
    <Button class="add">
      <span><AddIcon /> Add a currency</span>
    </Button>

    <ul>
      {#each balances as balance}
        <li class="balance">
          <div>
            <img src="/images/currency-flags/{balance.code.toLowerCase()}.png" alt="" />

            <p>
              <strong>{utils.formatCurrency(balance.amount)} {balance.code}</strong>
              <span>{balance.name ?? ""}</span>
            </p>
          </div>
        </li>
      {/each}
    </ul>
  </div>
</Layout>

<style>
  .balances {
    height: 100%;
    padding: 0 49px 30px;
  }

  .search > :global(*) {
    vertical-align: middle;
  }

  .balances > :global(button) {
    align-items: center;
    background-color: var(--color-white);
    border-radius: 10px;
    color: var(--color-gray-darkest);
    display: flex;
    font-size: 16px;
    font-weight: 400;
    height: unset;
    justify-content: space-between;
    margin-bottom: 8px;
    padding: 11px 28px;
    width: 100%;
  }

  .balances > :global(button::after),
  .balance::after {
    border: var(--color-gray-lighter) 1px solid;
    border-width: 2px 2px 0 0;
    content: "";
    display: block;
    height: 12px;
    transform: rotateZ(45deg);
    width: 12px;
  }

  .balances > :global(button > span > svg) {
    margin-right: 8px;
    vertical-align: middle;
  }

  .search > :global(.text-field) {
    background-color: transparent;
    border: 0;
    height: 100%;
    outline: 0;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 3px;
    width: 100%;
  }

  .balance {
    align-items: center;
    background-color: var(--color-white);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    padding: 11px 28px;
    width: 100%;
  }

  .balance:first-child {
    border-radius: 10px 10px 0 0;
  }

  .balance:last-child {
    border-radius: 0 0 10px 10px;
  }

  .balance > div {
    align-items: flex-start;
    display: flex;
  }

  img {
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 2px;
    margin-right: 17px;
    width: 30px;
  }

  p {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  p > span {
    color: var(--color-gray-lighter);
    font-size: 12px;
  }

  .search {
    background-color: var(--color-white);
    height: 100%;
    padding: 0 0 0 20px;
  }
</style>
