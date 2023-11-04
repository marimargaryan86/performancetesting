<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Table from "components/ui/table/table.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import { yymmdd } from "formatting/date-time";
  import { callAction, capitalize } from "utils/common";
  import TransactionDetails from "./transaction-details/transaction-details.svelte";
  import routeConfig from "routeConfig";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import type { PaginatedData } from "models/common";

  export let data;

  let selectedTransaction: Transaction | undefined = undefined;
  let bookingRequest: Promise<TripBooking | undefined> | undefined = undefined;

  $: transactions = data.transactions.data;

  function showDetails(transaction: Transaction): void {
    selectedTransaction = transaction;

    if (selectedTransaction) {
      bookingRequest = getBooking(selectedTransaction.externalReference);
    }
  }

  function deselectTransaction(): void {
    selectedTransaction = undefined;
    bookingRequest = undefined;
  }

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.transactions.cursor) {
      return { depleted: true };
    }

    const result = await callAction<{ transactions: PaginatedData<Transaction> }>({
      action: routeConfig.routes.pay.routes.activity.actions.listTransactions,
      data: { cursor: data.transactions.cursor },
      apply: false,
    });

    if (result.type === "success" && result.data) {
      data.transactions = {
        cursor: result.data.transactions.cursor,
        data: [...data.transactions.data, ...result.data.transactions.data],
      };

      return { depleted: !result.data.transactions.cursor };
    }

    return { depleted: true };
  };

  async function getBooking(externalReference: string): Promise<TripBooking | undefined> {
    const result = await callAction<{ booking: TripBooking }>({
      action: routeConfig.routes.pay.routes.activity.actions.getBooking,
      data: { bookingId: externalReference },
      apply: false,
    });

    if (result.type === "success") {
      return result.data?.booking;
    }

    return undefined;
  }
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
    <Header>Created</Header>
    <Header>Transaction type</Header>
    <Header>Payment type</Header>
    <Header>Payer</Header>
    <Header>Owed to us</Header>
    <Header>Beneficiary</Header>
    <Header>What we owe</Header>
    <Header>Sales Profit</Header>
    <Header>Reference</Header>
  </THead>

  <TBody>
    {#each transactions as item (item.id)}
      <TRow on:click={showDetails.bind(showDetails, item)}>
        <TCol maxWidth="96px" copyable>{item.externalReference}</TCol>
        <TCol>{yymmdd(item.createdAt)}</TCol>
        <TCol width="0">{capitalize(item.payment.method)}</TCol>
        <TCol width="0">{capitalize(item.payment.type)}</TCol>
        <TCompanyCol maxWidth="160px" companyName={item.payer?.name} />
        <TMoneyCol money={item.amounts.quotation} currencies={data.currencies} />
        <TCompanyCol maxWidth="160px" companyName={item.beneficiary?.name} />
        <TMoneyCol money={item.amounts.beneficiary} currencies={data.currencies} />
        <TMoneyCol money={item.sales.margin} currencies={data.currencies} />
        <TCol maxWidth="96px" copyable copyAlign="right">{item.invoiceReference ?? "Unknown"}</TCol>
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
