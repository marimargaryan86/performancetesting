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
  import StatusBadge from "components/ui/status-badge.svelte";
  import { amountAndCode } from "formatting/currency";
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

<table>
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
        <td>{amountAndCode(transaction.theyOwe)}</td>
        <td class="with-avatar">
          <EntityAvatar name={transaction.beneficiery} />
          <span>{transaction.beneficiery}</span>
        </td>
        <td>{amountAndCode(transaction.weOwe)}</td>
        <td>{amountAndCode(transaction.profit)}</td>
        <td>
          <button class="copy" on:click={createCopyFunc(transaction.reference)}>
            <span class="ellipsis">{transaction.reference}</span>
            <CopyIcon color="var(--color-primary-500)" />
          </button>
        </td>
        <td><StatusBadge value={transaction.status} /></td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  table {
    width: 100%;
    white-space: nowrap;
  }

  thead {
    position: sticky;
    top: 0;
    left: 0;
    width: 100%;
  }

  th {
    padding: 14px 8px 0;
    text-align: left;
    background-color: var(--color-generic-white);
  }

  th > :global(.sort-button) {
    width: 100%;
  }

  th::after {
    display: block;
    margin: 14px -8px 0;
    border-bottom: var(--color-neutral-200) 1px solid;
    content: "";
  }

  th:first-child::after {
    margin-left: -8px;
  }

  th:last-child::after {
    margin-right: -8px;
  }

  tbody {
    color: var(--color-neutral-800);
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }

  .ellipsis {
    max-width: 80px;
  }

  td {
    padding: 12px 8px;
  }

  td > :global(.status-badge) {
    width: 100%;
    vertical-align: middle;
  }

  tr > *:first-child {
    padding-left: 16px;
  }

  tr > *:last-child {
    padding-right: 16px;
  }

  td:first-child {
    border-radius: 8px 0 0 8px;
  }

  td:last-child {
    border-radius: 0 8px 8px 0;
  }

  tr:nth-child(even) > td {
    background-color: rgb(0 0 0 / 0.03);
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
