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
  import TCompanyCol from "components/ui/table/t-company-col.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type TransactionService from "integration/junction-hub-api/services/transaction-service";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";

  export let data;

  const i18n = getLocaleData();
  const locale = getLocale();

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
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.pay.title,
      $i18n.pages.pay.pages.activity.title,
      $i18n.pages.pay.pages.activity.pages.transactions.title,
    )}
  </title>
</svelte:head>

<Table class="transactions-table" {loadMore}>
  <THead>
    <Header>{$i18n.tableHeaders.id}</Header>
    <Header>{$i18n.tableHeaders.createdDate}</Header>
    <Header>{$i18n.tableHeaders.transactionType}</Header>
    <Header>{$i18n.tableHeaders.paymentType}</Header>
    <Header>{$i18n.tableHeaders.payer}</Header>
    <Header>{$i18n.tableHeaders.owedToUs}</Header>
    <Header>{$i18n.tableHeaders.beneficiary}</Header>
    <Header>{$i18n.tableHeaders.whatWeOwe}</Header>
    <Header>{$i18n.tableHeaders.salesProfit}</Header>
    <Header>{$i18n.tableHeaders.reference}</Header>
  </THead>

  <TBody>
    {#each transactions as item (item.id)}
      <TRow>
        <TCol maxWidth="96px" copyable>{item.externalReference}</TCol>
        <TCol>{item.createdAt.toLocaleDateString($locale)}</TCol>
        <TCol width="0">{$i18n.types[item.payment.method]}</TCol>
        <TCol width="0">{$i18n.types[item.payment.type]}</TCol>
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
</style>
