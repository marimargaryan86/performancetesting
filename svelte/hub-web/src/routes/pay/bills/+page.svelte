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
  import { browser } from "$app/environment";

  export let data;

  let searchQuery = "";

  $: ({ data: bills } = data.bills);
  $: searchQueryUuid = matchUuid(searchQuery) ? searchQuery : undefined;
  $: if (browser) {
    searchBills(searchQueryUuid);
  }

  async function searchBills(query?: string): Promise<void> {
    data.bills = await integrationInstancesClient.hub.bills.find({
      filter: { orderIds: query && matchUuid(query) ? [query] : undefined },
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
  <title>Bills · Pay · Junction Hub</title>
</svelte:head>

<StandardLayout pageTitle="Bills" bind:searchQuery>
  <Table {loadMore} class="bills-table">
    <THead>
      <Header>Order ID</Header>
      <Header>Owed to us</Header>
      <Header>Reconciled?</Header>
    </THead>
    <TBody>
      {#each bills as bill}
        <TRow>
          <TCol>{bill.orderId}</TCol>
          <TMoneyCol
            money={bill.amounts.total ?? { amount: 0, currency: "EUR" }}
            currencies={data.currencies}
          />
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
