<script lang="ts" context="module">
  export const LIST_CONVERSIONS_LIMIT = 20;
</script>

<script lang="ts">
  import { scrollLoad, type ScrollLoadFunc } from "$lib/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getLocale, getTranslator } from "$lib/i18n/index.js";
  import StatusBadge from "$lib/components/ui/status-badge.svelte";
  import { writable } from "svelte/store";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { slideFade } from "$lib/transitions/slide-fade";

  export let data;

  const t = getTranslator();
  const locale = getLocale();
  const pending = writable(false);

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
      $t("title"),
      $t("pages.pay.title"),
      $t("pages.pay.pages.activity.title"),
      $t("pages.pay.pages.activity.pages.conversions.title"),
    )}
  </title>
</svelte:head>

<x-table
  class="fx-table"
  use:scrollLoad={{ func: loadMore, pending }}
  style:grid-template-columns="repeat(10, minmax(min-content, 1fr))"
>
  <x-thead>
    <x-th>{$t("tableHeaders.id")}</x-th>
    <x-th>{$t("tableHeaders.createdDate")}</x-th>
    <x-th>{$t("tableHeaders.settlement")}</x-th>
    <x-th>{$t("tableHeaders.from")}</x-th>
    <x-th>{$t("tableHeaders.to")}</x-th>
    <x-th>{$t("tableHeaders.quoteRate")}</x-th>
    <x-th>{$t("tableHeaders.transactionRate")}</x-th>
    <x-th>{$t("tableHeaders.fxDelta")}</x-th>
    <x-th>{$t("tableHeaders.fxBuffer")}</x-th>
    <x-th>{$t("tableHeaders.status")}</x-th>
  </x-thead>

  {#each conversions as conversion (conversion.id)}
    <x-tr>
      <x-td>{conversion.transaction?.externalReference ?? ""}</x-td>
      <x-td>{conversion.createdAt?.toLocaleDateString($locale) ?? ""}</x-td>
      <x-td>{conversion.settledAt?.toLocaleDateString($locale) ?? ""}</x-td>
      <x-td>{conversion.amounts.sell?.currency ?? ""}</x-td>
      <x-td>{conversion.amounts.buy?.currency ?? ""}</x-td>
      <x-td>{conversion.transaction?.fx.quote ?? ""}</x-td>
      <x-td>{conversion.executedRate}</x-td>
      <x-td>{conversion.fx.delta ?? ""}</x-td>
      <x-td>{conversion.transaction?.fx.buffer ?? ""}</x-td>
      <x-td><StatusBadge value={conversion.fx.status ?? "unspecified"} /></x-td>
    </x-tr>
  {/each}

  {#if $pending}
    <x-tloading transition:slideFade={{ duration: 200 }}>
      <LoadingIcon color="var(--color-main-primary-500)" />
    </x-tloading>
  {/if}
</x-table>

<style>
  .fx-table {
    height: 100%;
  }

  x-td > :global(.status-badge) {
    width: 100%;
  }
</style>
