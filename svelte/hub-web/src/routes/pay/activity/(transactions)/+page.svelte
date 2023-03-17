<script lang="ts" context="module">
  function getMockTransactions(count: number): TransactionModel[] {
    return [...Array(count)].map(() => ({
      id: "abc123xyzmeepmeep",
      parentId: "abc123xyzmeepmeep",
      createdAt: new Date(),
      payer: ["ABC Travel", "ACME Agency", "Best OTA"][Math.floor(Math.random() * 3)] as string,
      theyOwe: {
        code: "USD",
        amount: Math.random() * 13000,
      },
      beneficiery: ["Air France", "Lufthansa", "Hilton", "British Airways"][
        Math.floor(Math.random() * 4)
      ] as string,
      weOwe: {
        code: "USD",
        amount: Math.random() * 13000,
      },
      profit: {
        code: "USD",
        amount: Math.random() * 13000,
      },
      reference: "ABC123XYZMEEPMEEP",
      status: ["paid", "cancelled", "pending"][Math.floor(Math.random() * 3)] as TransactionStatus,
    }));
  }
</script>

<script lang="ts">
  import CopyIcon from "components/icons/copy-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import SortButton from "components/ui/sort-button.svelte";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import { formatAmountAndCode } from "formatting/currency";
  import { yymmdd } from "formatting/date-time";
  import type { DirectionY } from "models/spatial";
  import type { TransactionModel, TransactionStatus } from "models/transaction";
  import type { PageData } from "./$types";

  export let data: PageData;

  const { searchQuery } = data;

  let sortBy: keyof TransactionModel = "id";
  let sortDirection: DirectionY = "down";

  $: transactions = getMockTransactions($searchQuery.length * 5 + 5);

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
          value="theyOwe"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Owed to us"
        />
      </th>
      <th>
        <SortButton
          value="beneficiery"
          bind:direction={sortDirection}
          bind:group={sortBy}
          label="Beneficiary"
        />
      </th>
      <th>
        <SortButton
          value="weOwe"
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
        <td class="with-avatar">
          <EntityAvatar name={transaction.payer} />
          <span>{transaction.payer}</span>
        </td>
        <td>{formatAmountAndCode(transaction.theyOwe)}</td>
        <td class="with-avatar">
          <EntityAvatar name={transaction.beneficiery} />
          <span>{transaction.beneficiery}</span>
        </td>
        <td>{formatAmountAndCode(transaction.weOwe)}</td>
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

  .with-avatar {
    display: flex;
    gap: 8px;
    align-items: center;
    font-weight: 600;
  }

  .copy {
    display: flex;
    gap: 0;
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

  .with-avatar > :global(.entity-avatar) {
    flex-shrink: 0;
  }
</style>
