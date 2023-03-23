<script lang="ts">
  import CopyIcon from "components/icons/copy-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import SortButton from "components/ui/sort-button.svelte";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import { filterTransactions } from "filters/transaction";
  import { formatAmountAndCode } from "formatting/currency";
  import { yymmdd } from "formatting/date-time";
  import type { DirectionY } from "models/spatial";
  import type { TransactionModel } from "models/transaction";
  import { sortTransactions } from "sorting/transactions";
  import type { PageData } from "./$types";

  export let data: PageData;

  const { searchQuery, status, dateRange } = data;

  let sortBy: keyof TransactionModel = "id";
  let sortDirection: DirectionY = "down";
  let transactions: TransactionModel[] = [];

  $: transactions = sortTransactions(
    filterTransactions(data.transactions, {
      query: $searchQuery,
      status: $status,
      dateRange: $dateRange,
    }),
    { by: sortBy, direction: sortDirection },
  );

  function createCopyFunc(value: string): () => void {
    return () => {
      navigator.clipboard.writeText(value);
    };
  }
</script>

<svelte:head>
  <title>Transactions · Activity · Pay · Junction Hub</title>
</svelte:head>

<table class="table-1">
  <thead>
    <tr>
      <th>
        <SortButton value="id" bind:direction={sortDirection} bind:group={sortBy} label="ID" />
      </th>
      <th>
        <SortButton
          value="parentId"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Parent ID"
        />
      </th>
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
          value="payer"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Payer"
        />
      </th>
      <th>
        <SortButton
          value="offerAmount"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Owed to us"
        />
      </th>
      <th>
        <SortButton
          value="beneficiary"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Beneficiary"
        />
      </th>
      <th>
        <SortButton
          value="beneficiaryAmount"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="What we owe"
        />
      </th>
      <th>
        <SortButton
          value="profit"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Sales profit"
        />
      </th>
      <th>
        <SortButton
          value="reference"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Reference"
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
        <td>
          <button class="copy" on:click={createCopyFunc(transaction.id)}>
            <span class="ellipsis">{transaction.id}</span>
            <CopyIcon color="var(--color-primary-500)" />
          </button>
        </td>
        <td>
          <button class="copy" on:click={createCopyFunc(transaction.parentId)}>
            <span class="ellipsis">{transaction.parentId}</span>
            <CopyIcon color="var(--color-primary-500)" />
          </button>
        </td>
        <td>{yymmdd(transaction.createdAt)}</td>
        <td>
          <div class="company">
            <EntityAvatar name={transaction.payer.name} />
            <span title={transaction.payer.name}>{transaction.payer.name}</span>
          </div>
        </td>
        <td>{formatAmountAndCode(transaction.offerAmount)}</td>
        <td>
          <div class="company">
            <EntityAvatar name={transaction.beneficiary.name} />
            <span title={transaction.beneficiary.name}>{transaction.beneficiary.name}</span>
          </div>
        </td>
        <td>{formatAmountAndCode(transaction.beneficiaryAmount)}</td>
        <td>{formatAmountAndCode(transaction.profit)}</td>
        <td>
          <button class="copy" on:click={createCopyFunc(transaction.reference)}>
            <span class="ellipsis">{transaction.reference}</span>
            <CopyIcon color="var(--color-primary-500)" />
          </button>
        </td>
        <td><TransactionStatusBadge value={transaction.status} /></td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table {
    width: 100%;
    white-space: nowrap;
  }

  .ellipsis {
    max-width: 80px;
  }

  td > :global(.status-badge) {
    width: 100%;
    vertical-align: middle;
  }

  .company {
    display: flex;
    gap: 8px;
    align-items: center;
    max-width: 140px;
  }

  .company > span {
    display: block;
    overflow: hidden;
    font-weight: 600;
    text-overflow: ellipsis;
  }

  .copy {
    display: flex;
    align-items: center;
    max-width: 80px;
    font-weight: inherit;
    font-size: inherit;
    font-family: inherit;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .copy > :global(svg) {
    flex-shrink: 0;
  }

  .copy:not(:hover) > :global(svg) {
    display: none;
  }

  .company > :global(.entity-avatar) {
    flex-shrink: 0;
  }
</style>
