<script lang="ts" context="module">
  export function queryFiltersGetter(value: JourneyFilterOptionsQuery): JourneyFilterOptions {
    return {
      bookingStatus: bookingStatuses.find((item) => item === value.bookingStatus),
      createdAtRange: parseDateRange(value["createdAt[from]"], value["createdAt[to]"]),
      departureAtRange: parseDateRange(value["departureAt[from]"], value["departureAt[to]"]),
      passengerLastName:
        value.passengerLastName === undefined || value.passengerLastName.length > 2
          ? value.passengerLastName
          : undefined,
      passengerNameRecord:
        value.passengerNameRecord === undefined ||
        validatePassengerNameRecord(value.passengerNameRecord)
          ? value.passengerNameRecord
          : undefined,
    };
  }
  export function queryFiltersValid(value: JourneyFilterOptions): {
    [key in keyof JourneyFilterOptions]?: boolean;
  } {
    return {
      passengerLastName:
        value.passengerLastName === undefined || value.passengerLastName.length > 2,
      passengerNameRecord:
        value.passengerNameRecord === undefined ||
        validatePassengerNameRecord(value.passengerNameRecord),
    };
  }

  export const LIST_JOURNEYS_LIMIT = 20;
  export const LIST_JOURNEYS_SORT: Parameters<JourneyService["find"]>[0]["sort"] = "-createdAt";

  function getOrderDepartureDate(order: Order): { date: Date; timeZone: string } {
    const departureLeg = order.bookings
      .flatMap((booking) => booking.detailsList.flatMap((details) => details.legs))
      .sort((a, b) => {
        return a.departureAt.getTime() - b.departureAt.getTime();
      })[0];

    if (!departureLeg) {
      throw new Error("Unknown departure date");
    }

    return {
      date: departureLeg.departureAt,
      timeZone: departureLeg.origin.timeZone,
    };
  }

  function getPassengerNames(order: Order): string[] {
    return order.passengers.map((passenger) => `${passenger.firstName} ${passenger.lastName}`);
  }

  function getTotalPrice(order: Order): Price {
    const prices = order.bookings.flatMap((booking) => booking.price.total);

    return prices.reduce((prev, curr) => ({
      amount: prev.amount + curr.amount,
      currency: curr.currency,
    }));
  }
</script>

<script lang="ts">
  import StandardLayout from "~/components/page/standard-layout.svelte";
  import { getOrderStatus } from "~/integration/common/schemas/order";
  import type { Order } from "~/integration/junction-hub-api/schemas/order";
  import type { Price } from "~/integration/common/schemas/price";
  import routeConfig from "~/route-config";
  import { scrollLoad, type ScrollLoadFunc } from "~/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import type JourneyService from "~/integration/junction-hub-api/services/journey-service";
  import type {
    JourneyFilterOptions,
    JourneyFilterOptionsQuery,
  } from "~/integration/junction-hub-api/schemas/journey";
  import Filters from "./filters.svelte";
  import { ensureDefined } from "~/utils/array";
  import { bookingStatuses } from "~/integration/junction-hub-api/schemas/booking";
  import { parseDateRange } from "~/utils/date-time";
  import { getPageTitle } from "~/utils/page-title";
  import { getLocale, getTranslator } from "~/i18n";
  import Icon from "~/components/icons/icon.svelte";
  import { getQueryStore } from "~/stores/query-store";
  import { writable } from "svelte/store";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";
  import { slideFade } from "~/transitions/slide-fade";
  import { formatAmount } from "$lib/formatting/currency";
  import StatusBadge from "~/components/ui/status-badge.svelte";
  import { validatePassengerNameRecord } from "~/utils/booking";
  import FindTripDialog from "~/components/modals/find-trip-dialog.svelte";

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
      href={routeConfig.routes.tripManagement.routes.book.routes.train.root}
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
        {@const cancellationStatus = getOrderStatus.cancellation(order)}
        {@const refundStatus = getOrderStatus.refund(order)}
        {@const bookingStatus = getOrderStatus.booking(order)}
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
