<script lang="ts" context="module">
  export const LIST_BILLS_LIMIT = 20;
</script>

<script lang="ts">
  import StandardLayout from "components/page/standard-layout.svelte";
  import Switch from "components/ui/switch.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type { Bill } from "integration/junction-hub-api/schemas/bill";
  import { match as matchUuid } from "../../../params/uuid";
  import { getLocaleData } from "i18n";
  import { browser } from "$app/environment";
  import { getPageTitle } from "utils/page-title";

  export let data;

  let searchQuery = "";

  const i18n = getLocaleData();

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
    {getPageTitle($i18n.title, $i18n.pages.pay.title, $i18n.pages.pay.pages.bills.title)}
  </title>
</svelte:head>

<StandardLayout pageTitle={$i18n.pages.pay.pages.bills.title} bind:searchQuery>
  <Table {loadMore} class="bills-table">
    <THead>
      <Header>{$i18n.tableHeaders.orderId}</Header>
      <Header>{$i18n.tableHeaders.createdDate}</Header>
      <Header>{$i18n.tableHeaders.updatedDate}</Header>
      <Header>{$i18n.tableHeaders.owedToUs}</Header>
      <Header textAlign="right">{$i18n.tableHeaders.reconciledQuestion}</Header>
    </THead>
    <TBody>
      {#each bills as bill}
        <TRow>
          <TCol width="0">{bill.orderId}</TCol>
          <TCol width="0">{bill.createdAt?.toLocaleDateString("sv-SE") ?? "N/A"}</TCol>
          <TCol width="0">{bill.updatedAt?.toLocaleDateString("sv-SE") ?? "N/A"}</TCol>
          {#if bill.amounts.total}
            <TMoneyCol money={bill.amounts.total} />
          {:else}
            <TCol width="0" />
          {/if}
          <TCol width="40px" textAlign="right">
            <Switch
              active={bill.reconciled}
              on:toggle={toggleReconciliation.bind(toggleReconciliation, bill)}
            />
          </TCol>
        </TRow>
      {/each}
    </TBody>
  </Table>
</StandardLayout>

<style>
  :global(.table.bills-table) {
    height: 100%;
  }
</style>
