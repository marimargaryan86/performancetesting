<script lang="ts" context="module">
  export const LIST_JOURNEYS_LIMIT = 20;
  export const LIST_JOURNEYS_SORT: Parameters<JourneyService["find"]>[0]["sort"] = "-createdAt";
</script>

<script lang="ts">
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import * as CommonSchemas from "~/integration/common/schemas";
  import routeConfig from "$lib/route-config";
  import { scrollLoad, type ScrollLoadFunc } from "$lib/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import type JourneyService from "~/integration/junction-hub-api/services/journey-service";
  import Filters, {
    queryFiltersGetter,
    queryFiltersValid,
  } from "$lib/components/pages/trip-management/orders/filters.svelte";
  import { ensureDefined } from "$lib/utils/array";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getLocale, getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";
  import { getQueryStore } from "$lib/stores/query-store";
  import { writable } from "svelte/store";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { formatAmount } from "$lib/formatting/currency";
  import StatusBadge from "$lib/components/ui/status-badge.svelte";
  import FindTripDialog from "$lib/components/modals/find-trip-dialog.svelte";
  import { getTotalPrice, getOrderDepartureDate, getPassengerNames } from "$lib/utils/order";

  export let data;

  let findTripDialog: FindTripDialog | undefined;

  const filters = getQueryStore({
    get: queryFiltersGetter,
    set: (value) => ({
      "createdAt[from]": value.createdAtRange?.from.toLocaleDateString("sv-SE"),
      "createdAt[to]": value.createdAtRange?.to.toLocaleDateString("sv-SE"),
      "departureAt[from]": value.departureAtRange?.from.toLocaleDateString("sv-SE"),
      "departureAt[to]": value.departureAtRange?.to.toLocaleDateString("sv-SE"),
      bookingStatus: value.bookingStatus,
      passengerLastName: value.passengerLastName,
      passengerNameRecord: value.passengerNameRecord,
    }),
    valid: queryFiltersValid,
  });
  const t = getTranslator();
  const locale = getLocale();
  const pending = writable(false);
  const columns =
    "repeat(4, minmax(max-content, 1fr)) minmax(160px, 1fr) 1fr repeat(3, min-content)";

  $: orders = data.journeys.data.flatMap((item) => item.orders);

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.journeys.cursor) {
      return { depleted: true };
    }

    const resp = await integrationInstancesClient.hub.journeys.find({
      cursor: data.journeys.cursor,
      limit: LIST_JOURNEYS_LIMIT,
      sort: LIST_JOURNEYS_SORT,
      filter: $filters,
    });

    data.journeys = {
      cursor: resp.cursor,
      data: [...data.journeys.data, ...resp.data],
    };

    return { depleted: !resp.cursor };
  };
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.orders.title"),
    )}
  </title>
</svelte:head>

<FindTripDialog bind:this={findTripDialog} />

<StandardLayout
  pageTitle={$t("pages.tripManagement.pages.orders.title")}
  filtersActive={Boolean(Object.values($filters).find(ensureDefined))}
>
  <div slot="actions">
    <button variant="outline" size="small" on:click={findTripDialog?.open}>
      <Icon variant="search" size="20px" />
      {$t("actions.findTrip")}
    </button>
    <a
      variant="primary"
      size="small"
      href={routeConfig.routes.tripManagement.routes.book.routes.rail.root}
    >
      <Icon variant="plus" size="20px" />
      {$t("actions.newOrder")}
    </a>
  </div>

  <Filters slot="filters" bind:filters={$filters} />

  {#if orders.length}
    <x-table
      class="orders-table"
      use:scrollLoad={{ func: loadMore, pending }}
      style:grid-template-columns={columns}
    >
      <x-thead>
        <x-th>{$t("tableHeaders.orderReference")}</x-th>
        <x-th>{$t("tableHeaders.createdDate")}</x-th>
        <x-th>{$t("tableHeaders.tickets")}</x-th>
        <x-th>{$t("tableHeaders.departureDate")}</x-th>
        <x-th>{$t("tableHeaders.passengers")}</x-th>
        <x-th>{$t("tableHeaders.totalPrice")}</x-th>
        <x-th>{$t("tableHeaders.bookingStatus")}</x-th>
        <x-th>{$t("tableHeaders.cancellationStatus")}</x-th>
        <x-th>{$t("tableHeaders.refundStatus")}</x-th>
      </x-thead>

      {#each orders as order (order.id)}
        {@const cancellationStatus = CommonSchemas.getOrderStatus.cancellation(order)}
        {@const refundStatus = CommonSchemas.getOrderStatus.refund(order)}
        {@const bookingStatus = CommonSchemas.getOrderStatus.booking(order)}
        {@const totalPrice = getTotalPrice(order)}
        {@const hasTickets = Boolean(order.bookings.flatMap((item) => item.ticketUrls).length)}
        {@const departureAt = getOrderDepartureDate(order)}

        <x-tr>
          <x-td>
            <a href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).root}>
              {order.journey?.reference ?? $t("words.unknown")}
            </a>
          </x-td>
          <x-td>{order.createdAt.toLocaleDateString($locale)}</x-td>
          <x-td>
            {#if hasTickets}
              <a
                href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).routes
                  .tickets.root}
                download
              >
                {$t("actions.download")}
              </a>
            {:else}
              <span class="not-available">{$t("words.notAvailable")}</span>
            {/if}
          </x-td>
          <x-td>
            {departureAt.date.toLocaleDateString($locale, { timeZone: departureAt.timeZone })}
          </x-td>
          <x-td weight="bold">{getPassengerNames(order).join(", ")}</x-td>
          <x-td>{formatAmount(totalPrice, $locale, { sign: true })}</x-td>
          <x-td>
            {#if bookingStatus}<StatusBadge value={bookingStatus} />{/if}
          </x-td>
          <x-td>
            {#if cancellationStatus}<StatusBadge value={cancellationStatus} />{/if}
          </x-td>
          <x-td>
            {#if refundStatus}<StatusBadge value={refundStatus} />{/if}
          </x-td>
        </x-tr>
      {/each}

      {#if $pending}
        <x-tloading transition:slideFade={{ duration: 200 }}>
          <LoadingIcon color="var(--color-main-primary-500)" />
        </x-tloading>
      {/if}
    </x-table>
  {:else}
    <div class="not-found-wrapper">
      <div class="not-found-container">
        <img src="/images/illustrations/not-found.png" alt="" />
        <h3 typography="headline-large" weight="bold">{$t("sentences.noTripsFound")}</h3>
        <pre typography="body-large">{$t("sentences.noTripsFoundMessage")}</pre>
      </div>
    </div>
  {/if}
</StandardLayout>

<style>
  .orders-table {
    height: 100%;
  }

  a:not([variant]) {
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .not-available {
    color: var(--color-common-light-soft);
  }

  x-td > :global(.status-badge) {
    width: 100%;
  }

  .not-found-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    background-color: var(--color-common-background-light-main);
  }

  .not-found-container {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: center;
    justify-content: center;
  }

  pre {
    color: var(--color-common-light-soft);
    text-align: center;
  }
</style>
