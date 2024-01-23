<script lang="ts" context="module">
  export const LIST_TRANSACTIONS_LIMIT = 20;
  export const LIST_TRANSACTIONS_SORT: Parameters<TransactionService["find"]>[0]["sort"] =
    "-createdAt";
</script>

<script lang="ts">
  import { scrollLoad, type ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type TransactionService from "integration/junction-hub-api/services/transaction-service";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";
  import { writable } from "svelte/store";
  import { slideFade } from "transitions/slide-fade";
  import { formatAmount } from "formatting/currency";
  import LoadingIcon from "components/icons/loading-icon.svelte";

  export let data;

  const i18n = getLocaleData();
  const locale = getLocale();
  const pending = writable(false);

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

<x-table
  class="transactions-table"
  style:grid-template-columns="repeat(10, minmax(max-content, 1fr))"
  use:scrollLoad={{ func: loadMore, pending }}
>
  <x-thead>
    <x-th>{$i18n.tableHeaders.id}</x-th>
    <x-th>{$i18n.tableHeaders.createdDate}</x-th>
    <x-th>{$i18n.tableHeaders.transactionType}</x-th>
    <x-th>{$i18n.tableHeaders.paymentType}</x-th>
    <x-th>{$i18n.tableHeaders.payer}</x-th>
    <x-th>{$i18n.tableHeaders.owedToUs}</x-th>
    <x-th>{$i18n.tableHeaders.beneficiary}</x-th>
    <x-th>{$i18n.tableHeaders.whatWeOwe}</x-th>
    <x-th>{$i18n.tableHeaders.salesProfit}</x-th>
    <x-th>{$i18n.tableHeaders.reference}</x-th>
  </x-thead>

  {#each transactions as item (item.id)}
    <x-tr>
      <x-td>{item.externalReference}</x-td>
      <x-td>{item.createdAt.toLocaleDateString($locale)}</x-td>
      <x-td>{$i18n.types[item.payment.method]}</x-td>
      <x-td>{$i18n.types[item.payment.type]}</x-td>
      <x-td class="company">
        {#if item.payer}
          <EntityAvatar name={item.payer.name} size="24px" /> {item.payer.name}
        {/if}
      </x-td>
      <x-td>{formatAmount(item.amounts.quotation, { locale: $locale, sign: true })}</x-td>
      <x-td class="company">
        {#if item.beneficiary}
          <EntityAvatar name={item.beneficiary.name} size="24px" /> {item.beneficiary.name}
        {/if}
      </x-td>
      <x-td>{formatAmount(item.amounts.beneficiary, { locale: $locale, sign: true })}</x-td>
      <x-td>{formatAmount(item.sales.margin, { locale: $locale, sign: true })}</x-td>
      <x-td>{item.invoiceReference ?? "Unknown"}</x-td>
    </x-tr>
  {/each}

  {#if $pending}
    <x-tloading transition:slideFade={{ duration: 200 }}>
      <LoadingIcon color="var(--color-main-primary-500)" />
    </x-tloading>
  {/if}
</x-table>

<style>
  .transactions-table {
    height: 100%;
  }
</style>
