<script lang="ts" context="module">
  export const LIST_TRANSACTIONS_LIMIT = 20;
  export const LIST_TRANSACTIONS_SORT: Parameters<TransactionService["find"]>[0]["sort"] =
    "-createdAt";
</script>

<script lang="ts">
  import { scrollLoad, type ScrollLoadFunc } from "~/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import type TransactionService from "~/integration/junction-hub-api/services/transaction-service";
  import EntityAvatar from "~/components/ui/entity-avatar.svelte";
  import { getPageTitle } from "~/utils/page-title";
  import { getLocale, getTranslator } from "~/i18n";
  import { writable } from "svelte/store";
  import { slideFade } from "~/transitions/slide-fade";
  import { formatAmount } from "~/formatting/currency";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";

  export let data;

  const t = getTranslator();
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
      $t("title"),
      $t("pages.pay.title"),
      $t("pages.pay.pages.activity.title"),
      $t("pages.pay.pages.activity.pages.transactions.title"),
    )}
  </title>
</svelte:head>

<x-table
  class="transactions-table"
  style:grid-template-columns="repeat(10, minmax(max-content, 1fr))"
  use:scrollLoad={{ func: loadMore, pending }}
>
  <x-thead>
    <x-th>{$t("tableHeaders.id")}</x-th>
    <x-th>{$t("tableHeaders.createdDate")}</x-th>
    <x-th>{$t("tableHeaders.transactionType")}</x-th>
    <x-th>{$t("tableHeaders.paymentType")}</x-th>
    <x-th>{$t("tableHeaders.payer")}</x-th>
    <x-th>{$t("tableHeaders.owedToUs")}</x-th>
    <x-th>{$t("tableHeaders.beneficiary")}</x-th>
    <x-th>{$t("tableHeaders.whatWeOwe")}</x-th>
    <x-th>{$t("tableHeaders.salesProfit")}</x-th>
    <x-th>{$t("tableHeaders.reference")}</x-th>
  </x-thead>

  {#each transactions as item (item.id)}
    <x-tr>
      <x-td>{item.externalReference}</x-td>
      <x-td>{item.createdAt.toLocaleDateString($locale)}</x-td>
      <x-td>{$t(`types.${item.payment.method}`)}</x-td>
      <x-td>{$t(`types.${item.payment.type}`)}</x-td>
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
