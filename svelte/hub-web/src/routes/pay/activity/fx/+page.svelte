<script lang="ts">
  import { yymmdd } from "formatting/date-time";
  import { callAction } from "utils/common";
  import Table from "components/ui/table/table.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import routeConfig from "routeConfig";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";

  export let form;
  export let data;

  $: conversions = data.conversions.data;

  async function loadMore(): Promise<void> {
    if (!data.conversions.cursor) {
      return;
    }

    await callAction({
      action: routeConfig.routes.pay.routes.activity.routes.conversions.actions.listConversions,
      data: {
        cursor: data.conversions.cursor,
      },
    });

    if (form?.conversions) {
      data.conversions = {
        cursor: form.conversions.cursor,
        data: [...data.conversions.data, ...form.conversions.data],
      };
    }
  }
</script>

<svelte:head>
  <title>FX · Activity · Pay · Junction Hub</title>
</svelte:head>

<Table class="fx-table" {loadMore}>
  <THead>
    <Header>ID</Header>
    <Header>Created</Header>
    <Header>Settlement</Header>
    <Header>From</Header>
    <Header>To</Header>
    <Header>Quote Rate</Header>
    <Header>Transaction Rate</Header>
    <Header>FX Delta</Header>
    <Header>FX Buffer</Header>
    <Header>Status</Header>
  </THead>

  <TBody>
    {#each conversions as conversion (conversion.id)}
      <TRow>
        <TCol maxWidth="96px" copyable>{conversion.transaction?.externalReference ?? ""}</TCol>
        <TCol class="currency typography bold">
          {conversion.createdAt ? yymmdd(conversion.createdAt) : ""}
        </TCol>
        <TCol class="currency typography bold">
          {conversion.settledAt ? yymmdd(conversion.settledAt) : ""}
        </TCol>
        <TCol class="currency typography bold">
          {conversion.amounts.sell?.currency ? conversion.amounts.sell.currency : ""}
        </TCol>
        <TCol class="currency typography bold">
          {conversion.amounts.buy?.currency ? conversion.amounts.buy.currency : ""}
        </TCol>
        <TCol>{conversion.transaction?.fx.quote ?? ""}</TCol>
        <TCol>{conversion.executedRate}</TCol>
        <TCol>{conversion.fx.delta ?? ""}</TCol>
        <TCol>{conversion.transaction?.fx.buffer ?? ""}</TCol>
        <TStatusBadgeCol value={conversion.fx.status ?? "unspecified"} />
      </TRow>
    {/each}
  </TBody>
</Table>

<style>
  :global(.table.fx-table) {
    width: 100%;
    height: 100%;
  }

  :global(.table.fx-table .currency) {
    color: var(--color-main-neutral-600);
  }

  :global(.table.fx-table .status-badge) {
    width: 100%;
  }
</style>
