<script lang="ts" context="module">
  export const LIST_BILLS_LIMIT = 20;
</script>

<script lang="ts">
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import Switch from "~/components/ui/switch.svelte";
  import { scrollLoad, type ScrollLoadFunc } from "~/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import type { Bill } from "~/integration/junction-hub-api/schemas/bill";
  import { match as matchUuid } from "../../../params/uuid";
  import { getLocale, getTranslator } from "~/i18n";
  import { browser } from "$app/environment";
  import { getPageTitle } from "~/utils/page-title";
  import { formatAmount } from "$lib/formatting/currency";
  import { writable } from "svelte/store";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import { slideFade } from "~/transitions/slide-fade";

  export let data;

  let searchQuery = "";

  const locale = getLocale();
  const t = getTranslator();
  const pending = writable(false);

  $: ({ data: bills } = data.bills);
  $: searchQueryUuid = matchUuid(searchQuery) ? searchQuery : undefined;
  $: if (browser) {
    searchBills(searchQueryUuid);
  }

  async function searchBills(query?: string): Promise<void> {
    data.bills = await integrationInstancesClient.hub.bills.find({
      filter: { orderIds: query && matchUuid(query) ? [query] : undefined },
      limit: LIST_BILLS_LIMIT,
    });
  }

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.bills.cursor) {
      return { depleted: true };
    }

    let orderIds: string[] | undefined;

    if (matchUuid(searchQuery)) {
      orderIds = [searchQuery];
    }

    const nextBills = await integrationInstancesClient.hub.bills.find({
      cursor: data.bills.cursor,
      filter: { orderIds },
      limit: LIST_BILLS_LIMIT,
    });

    data.bills = {
      data: [...data.bills.data, ...nextBills.data],
      cursor: nextBills.cursor,
    };

    return { depleted: !nextBills.cursor };
  };

  async function toggleReconciliation(bill: Bill): Promise<void> {
    await integrationInstancesClient.hub.bills.toggleReconciliation({ bill });

    bill.reconciled = !bill.reconciled;
  }
</script>

<svelte:head>
  <title>
    {getPageTitle($t("title"), $t("pages.pay.title"), $t("pages.pay.pages.bills.title"))}
  </title>
</svelte:head>

<StandardLayout pageTitle={$t("pages.pay.pages.bills.title")} bind:searchQuery>
  <x-table
    class="bills-table"
    style:grid-template-columns="repeat(4, minmax(max-content, 1fr)) min-content"
    use:scrollLoad={{ func: loadMore, pending }}
  >
    <x-thead>
      <x-th>{$t("tableHeaders.orderId")}</x-th>
      <x-th>{$t("tableHeaders.createdDate")}</x-th>
      <x-th>{$t("tableHeaders.updatedDate")}</x-th>
      <x-th>{$t("tableHeaders.owedToUs")}</x-th>
      <x-th>{$t("tableHeaders.reconciledQuestion")}</x-th>
    </x-thead>

    {#each bills as bill}
      <x-tr>
        <x-td>{bill.orderId}</x-td>
        <x-td>{bill.createdAt?.toLocaleDateString($locale) ?? $t("words.notAvailable")}</x-td>
        <x-td>{bill.updatedAt?.toLocaleDateString($locale) ?? $t("words.notAvailable")}</x-td>
        <x-td>
          {#if bill.amounts.total}
            {formatAmount(bill.amounts.total, $locale, { sign: true })}
          {/if}
        </x-td>
        <x-tactions>
          <Switch
            active={bill.reconciled}
            on:toggle={toggleReconciliation.bind(toggleReconciliation, bill)}
          />
        </x-tactions>
      </x-tr>
    {/each}

    {#if $pending}
      <x-tloading transition:slideFade={{ duration: 200 }}>
        <LoadingIcon color="var(--color-main-primary-500)" />
      </x-tloading>
    {/if}
  </x-table>
</StandardLayout>

<style>
  .bills-table {
    height: 100%;
  }
</style>
