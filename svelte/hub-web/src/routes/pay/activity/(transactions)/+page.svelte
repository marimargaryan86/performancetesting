<script lang="ts" context="module">
  import type { DateRange } from "models/date-time";
  import type { TransactionModel, TransactionStatus } from "models/transaction";

  export const dateRange = writable<DateRange | undefined>(undefined);
  export const status = writable<TransactionStatus[]>([]);
  export const searchQuery = writable("");
</script>

<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Table from "components/ui/table/table.svelte";
  import type { PageData } from "./$types";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import { yymmdd } from "formatting/date-time";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import type { FlattenedObject } from "utils/common";
  import type { DirectionY } from "models/spatial";
  import { sortTransactions } from "sorting/transaction";
  import { filterTransactions } from "filters/transaction";
  import { formatAmount } from "formatting/currency";
  import { writable } from "svelte/store";
  import { onMount } from "svelte";
  import TransactionDetails from "./transaction-details/transaction-details.svelte";
  import integrationInstances from "integration-instances";

  export let data: PageData;

  let sortGroup: FlattenedObject<TransactionModel> = "createdAt";
  let sortDirection: DirectionY = "down";
  let selectedTransaction: TransactionModel | undefined = undefined;

  $: transactions = sortTransactions(
    filterTransactions(data.transactions, {
      query: $searchQuery,
      status: $status,
      dateRange: $dateRange,
    }),
    { by: sortGroup, direction: sortDirection },
  );

  function createShowDetailsFunc(id: string): () => void {
    return () => {
      selectedTransaction = transactions.find((item) => item.id === id);
    };
  }

  async function loadMore(): Promise<void> {
    if (!data.transactionsCursor) {
      return;
    }

    const [nextTransactions, cursor] =
      await integrationInstances.junctionPay.transactions.listTransactions(
        data.token as string,
        data.transactionsCursor,
      );

    data.transactionsCursor = cursor;
    data.transactions = [...data.transactions, ...nextTransactions];
  }

  onMount(() => {
    $searchQuery = "";
    $dateRange = undefined;
    $status = [];
  });
</script>

<svelte:head>
  <title>Transactions · Activity · Pay · Junction Hub</title>
</svelte:head>

<TransactionDetails bind:transaction={selectedTransaction} />

<Table class="transactions-table" {loadMore}>
  <THead>
    <Header>ID</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="createdAt">Created</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="payer.name">Payer</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="amounts.quotation.amount">
      Owed to us
    </Header>
    <Header bind:sortGroup bind:sortDirection sortValue="beneficiary.name">Beneficiary</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="amounts.beneficiary.amount">
      What we owe
    </Header>
    <Header bind:sortGroup bind:sortDirection sortValue="amounts.salesMargin.amount">
      Sales Profit
    </Header>
    <Header>Reference</Header>
    <Header bind:sortGroup bind:sortDirection sortValue="status">Status</Header>
  </THead>

  <TBody>
    {#each transactions as item}
      <TRow on:click={createShowDetailsFunc(item.id)}>
        <TCol maxWidth="96px" copyable>{item.bookingId}</TCol>
        <TCol>{yymmdd(item.createdAt)}</TCol>
        <TCol maxWidth="160px">
          {#if item.payer}
            <div class="company">
              <EntityAvatar name={item.payer.name} size="26px" />
              <span>
                {item.payer.name}
              </span>
            </div>
          {/if}
        </TCol>
        <TCol>
          <div class="money">
            <span>{formatAmount(item.amounts.quotation, data.currencies)}</span>
            <strong class="typography body-small">{item.amounts.quotation.currency}</strong>
          </div>
        </TCol>
        <TCol maxWidth="160px">
          {#if item.beneficiary}
            <div class="company">
              <EntityAvatar name={item.beneficiary.name} size="26px" />
              <span>
                {item.beneficiary.name}
              </span>
            </div>
          {/if}
        </TCol>
        <TCol>
          <div class="money">
            <span>{formatAmount(item.amounts.beneficiary, data.currencies)}</span>
            <strong class="typography body-small">{item.amounts.beneficiary.currency}</strong>
          </div>
        </TCol>
        <TCol>
          <div class="money">
            <span>{formatAmount(item.amounts.salesMargin, data.currencies)}</span>
            <strong class="typography body-small">{item.amounts.salesMargin.currency}</strong>
          </div>
        </TCol>
        <TCol maxWidth="96px" copyable copyAlign="right">{item.reference}</TCol>
        <TCol width="80px">
          <TransactionStatusBadge value={item.status} />
        </TCol>
      </TRow>
    {/each}
  </TBody>
</Table>

<style>
  :global(.table.transactions-table) {
    width: 100%;
    height: 100%;
  }

  :global(.table.transactions-table .status-badge) {
    width: 100%;
  }

  :global(.table.transactions-table tbody tr) {
    cursor: pointer;
  }

  .company {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
  }

  .company > :global(.entity-avatar) {
    flex-shrink: 0;
  }

  .company > span {
    min-width: 0;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .money {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .money > strong {
    color: var(--color-main-neutral-600);
  }
</style>
