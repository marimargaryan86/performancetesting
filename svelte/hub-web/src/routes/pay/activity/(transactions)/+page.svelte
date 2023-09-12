<script lang="ts" context="module">
  import type { DateRange } from "models/date-time";

  export const dateRange = writable<DateRange | undefined>(undefined);
  export const status = writable<TransactionStatus[]>([]);
  export const searchQuery = writable("");
</script>

<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Table from "components/ui/table/table.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import { yymmdd } from "formatting/date-time";
  import TransactionStatusBadge from "components/ui/transaction-status-badge.svelte";
  import { callAction, type FlattenedObject } from "utils/common";
  import type { DirectionY } from "models/spatial";
  import { sortTransactions } from "sorting/transaction";
  import { filterTransactions } from "filters/transaction";
  import { writable } from "svelte/store";
  import { onMount } from "svelte";
  import TransactionDetails from "./transaction-details/transaction-details.svelte";
  import type { BookingModel } from "models/booking";
  import routeConfig from "routeConfig";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import type {
    TransactionModel,
    TransactionStatus,
  } from "integration/junction-pay/schemas/transaction";

  export let data;
  export let form;

  let sortGroup: FlattenedObject<TransactionModel> = "createdAt";
  let sortDirection: DirectionY = "down";
  let selectedTransaction: TransactionModel | undefined = undefined;
  let bookingRequest: Promise<BookingModel | undefined> | undefined = undefined;

  $: transactions = sortTransactions(
    filterTransactions(data.transactions.data, {
      query: $searchQuery,
      status: $status,
      dateRange: $dateRange,
    }),
    { by: sortGroup, direction: sortDirection },
  );

  function showDetails(transaction: TransactionModel): void {
    selectedTransaction = transaction;

    if (selectedTransaction) {
      bookingRequest = getBooking(selectedTransaction.bookingId);
    }
  }

  function deselectTransaction(): void {
    selectedTransaction = undefined;
    bookingRequest = undefined;
  }

  async function loadMore(): Promise<void> {
    if (!data.transactions.cursor) {
      return;
    }

    await callAction({
      action: routeConfig.pay.activity.actions.listTransactions,
      data: {
        cursor: data.transactions.cursor,
      },
    });

    if (form?.transactions) {
      data.transactions = {
        cursor: form.transactions.cursor,
        data: [...data.transactions.data, ...form.transactions.data],
      };
    }
  }

  async function getBooking(bookingId: string): Promise<BookingModel | undefined> {
    await callAction({ action: routeConfig.pay.activity.actions.getBooking, data: { bookingId } });

    return form?.booking;
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

{#if selectedTransaction}
  <TransactionDetails
    transaction={selectedTransaction}
    {bookingRequest}
    on:close={deselectTransaction}
  />
{/if}

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
    {#each transactions as item (item.id)}
      <TRow on:click={showDetails.bind(showDetails, item)}>
        <TCol maxWidth="96px" copyable>{item.bookingId}</TCol>
        <TCol>{yymmdd(item.createdAt)}</TCol>
        <TCompanyCol maxWidth="160px" companyName={item.payer?.name} />
        <TMoneyCol money={item.amounts.quotation} currencies={data.currencies} />
        <TCompanyCol maxWidth="160px" companyName={item.beneficiary?.name} />
        <TMoneyCol money={item.amounts.beneficiary} currencies={data.currencies} />
        <TMoneyCol money={item.amounts.salesMargin} currencies={data.currencies} />
        <TCol maxWidth="96px" copyable copyAlign="right">{item.reference}</TCol>
        <TCol width="80px"><TransactionStatusBadge value={item.status} /></TCol>
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
</style>
