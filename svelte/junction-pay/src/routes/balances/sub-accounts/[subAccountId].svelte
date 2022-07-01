<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import balanceAccounts from "$content/balance-accounts";
  import transactionData from "$content/transactions";
  import DatePicker from "$lib/components/date-picker/date-picker.svelte";
  import Table from "$lib/components/table.svelte";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";
  import { onMount } from "svelte";
  import Main from "../_layout.svelte";

  const transactions = transactionData;

  $: ({ subAccountId } = $page.params);
  $: subAccount = balanceAccounts.find((ba) => ba.id === subAccountId);

  onMount(() => {
    if (!subAccount) {
      goto(routeConfig.balances.subAccounts);
    }
  });
</script>

<svelte:head>
  <title>Junction | Sub Account {subAccount?.name}</title>
</svelte:head>

<Main>
  <div class="sub-account" slot="body">
    <h1>Transactions</h1>

    <form class="filters" on:submit|preventDefault>
      <label for="created-at-date">Created at</label>
      <DatePicker id="created-at-date" span />
    </form>

    <Table>
      <thead>
        <tr>
          <th>Reference</th>
          <th>Created</th>
          <th>Completed</th>
          <th>Type</th>
          <th>Status</th>
          <th>Amount</th>
          <th>Balance</th>
        </tr>
      </thead>

      <tbody>
        {#each transactions as transaction}
          <tr>
            <td>{transaction.ref}</td>
            <td>{utils.formatDate(transaction.createdAt, 1)}</td>
            <td>
              {transaction.completedAt ? utils.formatDate(transaction.completedAt, 1) : "N/A"}
            </td>
            <td>{transaction.type}</td>
            <td>{transaction.status}</td>
            <td>{transaction.amount.code} {utils.formatCurrency(transaction.amount.amount)}</td>
            <td>{transaction.amount.code} {utils.formatCurrency(transaction.balance.amount)}</td>
          </tr>
        {/each}
      </tbody>
    </Table>
  </div>
</Main>

<style>
  .sub-account {
    padding: 0 49px 30px;
  }

  h1 {
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 17px;
  }

  .filters {
    background-color: var(--color-white);
    border-radius: 10px;
    margin-bottom: 20px;
    padding: 16px 20px;
  }

  .filters > label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
    width: max-content;
  }

  .sub-account > :global(table) {
    width: 100%;
  }
</style>
