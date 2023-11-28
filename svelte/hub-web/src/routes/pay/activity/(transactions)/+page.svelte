<script lang="ts" context="module">
  export const LIST_TRANSACTIONS_LIMIT = 20;
  export const LIST_TRANSACTIONS_SORT: Parameters<TransactionService["find"]>[0]["sort"] =
    "-createdAt";
</script>

<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Table from "components/ui/table/table.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import { yymmdd } from "formatting/date-time";
  import { capitalize } from "utils/common";
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type TransactionService from "integration/junction-hub-api/services/transaction-service";

  export let data;

  $: transactions = data.transactions.data;

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.transactions.cursor) {
      return { depleted: true };
    }

    const nextTransactions = await integrationInstancesClient.hub.transactions.find({
      cursor: data.transactions.cursor,
      limit: LIST_TRANSACTIONS_LIMIT,
      sort: LIST_TRANSACTIONS_SORT,
    });

    data.transactions = {
      data: [...data.transactions.data, ...nextTransactions.data],
      cursor: nextTransactions.cursor,
    };

    return { depleted: !nextTransactions.cursor };
  };
</script>

<svelte:head>
  <title>Transactions · Activity · Pay · Junction Hub</title>
</svelte:head>

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
      <TRow>
        <TCol maxWidth="96px" copyable>{item.externalReference}</TCol>
        <TCol>{yymmdd(item.createdAt)}</TCol>
        <TCol width="0">{capitalize(item.payment.method)}</TCol>
        <TCol width="0">{capitalize(item.payment.type)}</TCol>
        <TCompanyCol maxWidth="160px" companyName={item.payer?.name} />
        <TMoneyCol money={item.amounts.quotation} />
        <TCompanyCol maxWidth="160px" companyName={item.beneficiary?.name} />
        <TMoneyCol money={item.amounts.beneficiary} />
        <TMoneyCol money={item.sales.margin} />
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
