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
  import type { Bill } from "integration/junction-hub-api/schemas/bill";
  import type { PaginatedData } from "models/common";
  import routeConfig from "routeConfig";
  import { callAction } from "utils/common";

  export let data;

  $: ({ data: bills } = data.bills);

  async function loadMore(): Promise<void> {
    if (!data.bills.cursor) {
      return;
    }

    const result = await callAction<{ bills: PaginatedData<Bill> }>({
      action: routeConfig.routes.pay.routes.bills.actions.listBills,
      data: { cursor: data.bills.cursor },
      apply: false,
    });

    if (result.type === "success" && result.data?.bills) {
      data.bills = {
        cursor: result.data.bills.cursor,
        data: [...data.bills.data, ...result.data.bills.data],
      };
    }
  }

  async function toggleReconciliation(bill: Bill): Promise<void> {
    await callAction({
      action: routeConfig.routes.pay.routes.bills.actions.toggleReconciliation,
      apply: false,
      data: { billId: bill.id },
    });
  }
</script>

<svelte:head>
  <title>Bills · Pay · Junction Hub</title>
</svelte:head>

<StandardLayout pageTitle="Bills" searchQuery="">
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
              bind:active={bill.reconciled}
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
