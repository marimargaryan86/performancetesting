<script lang="ts" context="module">
  export const LIST_CONVERSIONS_LIMIT = 20;
</script>

<script lang="ts">
  import Table from "components/ui/table/table.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";

  export let data;

  const i18n = getLocaleData();
  const locale = getLocale();

  $: conversions = data.conversions.data;

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.conversions.cursor) {
      return { depleted: true };
    }

    const nextConversions = await integrationInstancesClient.hub.conversions.find({
      cursor: data.conversions.cursor,
      limit: LIST_CONVERSIONS_LIMIT,
    });

    data.conversions = {
      data: [...data.conversions.data, ...nextConversions.data],
      cursor: nextConversions.cursor,
    };

    return { depleted: !nextConversions.cursor };
  };
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.pay.title,
      $i18n.pages.pay.pages.activity.title,
      $i18n.pages.pay.pages.activity.pages.conversions.title,
    )}
  </title>
</svelte:head>

<Table class="fx-table" {loadMore}>
  <THead>
    <Header>{$i18n.tableHeaders.id}</Header>
    <Header>{$i18n.tableHeaders.createdDate}</Header>
    <Header>{$i18n.tableHeaders.settlement}</Header>
    <Header>{$i18n.tableHeaders.from}</Header>
    <Header>{$i18n.tableHeaders.to}</Header>
    <Header>{$i18n.tableHeaders.quoteRate}</Header>
    <Header>{$i18n.tableHeaders.transactionRate}</Header>
    <Header>{$i18n.tableHeaders.fxDelta}</Header>
    <Header>{$i18n.tableHeaders.fxBuffer}</Header>
    <Header>{$i18n.tableHeaders.status}</Header>
  </THead>

  <TBody>
    {#each conversions as conversion (conversion.id)}
      <TRow>
        <TCol maxWidth="96px" copyable={Boolean(conversion.transaction?.externalReference)}>
          {conversion.transaction?.externalReference ?? ""}
        </TCol>
        <TCol class="currency" weight="bold">
          {conversion.createdAt?.toLocaleDateString($locale) ?? ""}
        </TCol>
        <TCol class="currency" weight="bold">
          {conversion.settledAt?.toLocaleDateString($locale) ?? ""}
        </TCol>
        <TCol class="currency" weight="bold">
          {conversion.amounts.sell?.currency ?? ""}
        </TCol>
        <TCol class="currency" weight="bold">
          {conversion.amounts.buy?.currency ?? ""}
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
