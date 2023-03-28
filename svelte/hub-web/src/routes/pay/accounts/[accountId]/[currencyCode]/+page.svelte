<script lang="ts" context="module">
  import {
    balanceTransactionStatus,
    type BalanceTransactionModel,
    type BalanceTransactionStatus,
  } from "models/transaction";

  function getMockTransactions(count: number): BalanceTransactionModel[] {
    return [...Array(count)].map(() => ({
      createdAt: new Date(),
      action: "FX Conversion",
      reason: "BA Payment",
      balance: {
        currency: "USD",
        amount: Math.random() * 13000,
      },
      credit: {
        currency: "USD",
        amount: Math.random() * 13000,
      },
      debit: {
        currency: "USD",
        amount: Math.random() * 13000,
      },
      status: ["completed", "deleted", "pending"][
        Math.floor(Math.random() * 3)
      ] as BalanceTransactionStatus,
    }));
  }
</script>

<script lang="ts">
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SortButton from "components/ui/sort-button.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatAmount } from "formatting/currency";
  import { yymmdd } from "formatting/date-time";
  import { formatBalanceTransactionStatus } from "formatting/transaction";
  import type { DateRange } from "models/date-time";
  import type { DirectionY } from "models/spatial";
  import type { PageData } from "./$types";
  import BalanceTransactionStatusBadge from "components/ui/balance-transaction-status-badge.svelte";
  import type { FlattenedObject } from "utils/common";

  export let data: PageData;

  let searchQuery = "";
  let dateRange: DateRange | undefined = undefined;
  let status: BalanceTransactionStatus[] = [];
  let sortDirection: DirectionY = "down";
  let sortBy: FlattenedObject<BalanceTransactionModel> = "createdAt";

  $: transactions = getMockTransactions(5 + searchQuery.length * 5);
</script>

<div class="transactions-page">
  <div class="header">
    <ul class="layout tabs">
      <li class="layout tab active">Transactions</li>
    </ul>

    <div class="balance">
      <CurrencyFlag code={data.balance.currency} />
      <span>{formatAmount(data.balance)}</span>
      <strong>{data.balance.currency.toUpperCase()}</strong>
    </div>
  </div>

  <div class="filters">
    <TextField placeholder="Search" bind:value={searchQuery}>
      <SearchIcon slot="icon-before" color="var(--color-neutral-400)" />
    </TextField>

    <DatePicker range bind:value={dateRange} placeholder="Date range" />

    <StatusPicker
      statuses={balanceTransactionStatus}
      format={formatBalanceTransactionStatus}
      bind:value={status}
      placeholder="Status"
    />
  </div>

  <div class="transactions">
    <table class="table-1">
      <thead>
        <tr>
          <th>
            <SortButton
              value="createdAt"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Date created"
            />
          </th>
          <th>
            <SortButton
              value="action"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Action"
            />
          </th>
          <th>
            <SortButton
              value="reason"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Reason"
            />
          </th>
          <th>
            <SortButton
              value="debit"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Debit"
            />
          </th>
          <th>
            <SortButton
              value="credit"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Credit"
            />
          </th>
          <th>
            <SortButton
              value="balance"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Balance"
            />
          </th>
          <th>
            <SortButton
              value="status"
              bind:direction={sortDirection}
              bind:group={sortBy}
              label="Status"
            />
          </th>
        </tr>
      </thead>

      <tbody>
        {#each transactions as transaction}
          <tr>
            <td>{yymmdd(transaction.createdAt)}</td>
            <td>{transaction.action}</td>
            <td>{transaction.reason}</td>
            <td>+{formatAmount(transaction.debit)}</td>
            <td>-{formatAmount(transaction.credit)}</td>
            <td>{formatAmount(transaction.balance)}</td>
            <td><BalanceTransactionStatusBadge value={transaction.status} /></td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

<style>
  .transactions-page {
    margin: -8px;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .balance {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--color-neutral-800);
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
  }

  .balance > span {
    font-weight: 700;
    font-size: 20px;
  }

  .balance > strong {
    font-weight: 500;
    font-size: 10px;
    letter-spacing: 2px;
  }

  .filters {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }

  .filters > :global(.text-field),
  .filters > :global(.date-picker),
  .filters > :global(.status-picker) {
    --height: 40px;
    --font-size: 12px;
  }

  .filters > :global(.text-field) {
    width: 100%;
    max-width: 240px;
  }

  @media screen and (max-width: 1439px) {
    .filters > :global(.text-field) {
      max-width: 158px;
    }
  }

  .transactions {
    height: calc(100vh - 256px);
    margin: 0 -16px -24px;
    padding: 0 8px 8px;
    overflow: auto;
    background-color: var(--color-generic-white);
    border-radius: 0 0 8px 8px;
  }

  table {
    width: 100%;
    white-space: nowrap;
  }

  td > :global(.status-badge) {
    width: 100%;
    vertical-align: middle;
  }
</style>
