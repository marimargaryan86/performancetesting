<script lang="ts" context="module">
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

  const filters = createQueryStore<JourneyFilterOptions, JourneyFilterOptionsQuery>(
    (data) => ({
      "createdAt[from]": data.createdAtRange?.from.toLocaleDateString("sv-SE"),
      "createdAt[to]": data.createdAtRange?.to.toLocaleDateString("sv-SE"),
      "departureAt[from]": data.departureAtRange?.from.toLocaleDateString("sv-SE"),
      "departureAt[to]": data.departureAtRange?.to.toLocaleDateString("sv-SE"),
      bookingStatus: data.bookingStatus,
      referenceNumber: data.referenceNumber,
      passengerLastName: data.passengerLastName,
    }),
    (query) => ({
      bookingStatus: bookingStatuses.includes(query.bookingStatus as BookingStatus)
        ? (query.bookingStatus as BookingStatus)
        : undefined,
      createdAtRange: parseDateRange(query["createdAt[from]"], query["createdAt[to]"]),
      departureAtRange: parseDateRange(query["departureAt[from]"], query["departureAt[to]"]),
      referenceNumber: query.referenceNumber,
      passengerLastName: query.passengerLastName,
    }),
  );
</script>

<script lang="ts">
  import PlusIcon from "components/icons/plus-icon.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import Button from "components/ui/button.svelte";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";
  import Table from "components/ui/table/table.svelte";
  import { getOrderStatus } from "integration/common/schemas/order";
  import type { Order } from "integration/junction-hub-api/schemas/order";
  import type { Price } from "integration/common/schemas/price";
  import routeConfig from "routeConfig";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type JourneyService from "integration/junction-hub-api/services/journey-service";
  import type {
    JourneyFilterOptions,
    JourneyFilterOptionsQuery,
  } from "integration/junction-hub-api/schemas/journey";
  import Filters from "./filters.svelte";
  import { ensureDefined } from "utils/array";
  import { createQueryStore } from "utils/url";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import { parseDateRange } from "utils/date-time";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";

  export let data;

  let searchQuery = "";

  const i18n = getLocaleData();
  const locale = getLocale();

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
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.orders.title,
    )}
  </title>
</svelte:head>

<StandardLayout
  pageTitle={$i18n.pages.tripManagement.pages.orders.title}
  bind:searchQuery
  filtersActive={Boolean(Object.values($filters).find(ensureDefined))}
>
  <Button size="small" href={routeConfig.routes.tripManagement.routes.book.root} slot="actions">
    {$i18n.actions.newOrder}
    <PlusIcon />
  </Button>

  <Filters slot="filters" bind:filters={$filters} />

  <Table class="orders-table" {loadMore}>
    <THead>
      <Header>{$i18n.tableHeaders.orderReference}</Header>
      <Header>{$i18n.tableHeaders.createdDate}</Header>
      <Header>{$i18n.tableHeaders.tickets}</Header>
      <Header>{$i18n.tableHeaders.departureDate}</Header>
      <Header>{$i18n.tableHeaders.passengers}</Header>
      <Header>{$i18n.tableHeaders.totalPrice}</Header>
      <Header>{$i18n.tableHeaders.bookingStatus}</Header>
      <Header>{$i18n.tableHeaders.cancellationStatus}</Header>
      <Header>{$i18n.tableHeaders.refundStatus}</Header>
    </THead>

    <TBody>
      {#each orders as order (order.id)}
        {@const cancellationStatus = getOrderStatus.cancellation(order)}
        {@const refundStatus = getOrderStatus.refund(order)}
        {@const bookingStatus = getOrderStatus.booking(order)}
        {@const totalPrice = getTotalPrice(order)}
        {@const hasTickets = Boolean(order.bookings.flatMap((item) => item.ticketUrls).length)}
        {@const departureAt = getOrderDepartureDate(order)}

        <TRow alternatingBackground={false}>
          <TCol class="typography body-small" width="0">
            <a href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).root}>
              {order.journey?.reference ?? $i18n.words.unknown}
            </a>
          </TCol>
          <TCol class="typography body-small" width="0">
            {order.createdAt.toLocaleDateString($locale)}
          </TCol>
          <TCol class="typography body-small" width="0">
            {#if hasTickets}
              <a
                class="typography body-small"
                href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).routes
                  .tickets.root}
                download
              >
                {$i18n.actions.download}
              </a>
            {:else}
              <span class="not-available">{$i18n.words.notAvailable}</span>
            {/if}
          </TCol>
          <TCol class="typography body-small" width="0">
            {departureAt.date.toLocaleDateString($locale, { timeZone: departureAt.timeZone })}
          </TCol>
          <TCol class="typography body-small bold" maxWidth="240px">
            {getPassengerNames(order).join(", ")}
          </TCol>
          <TMoneyCol class="typography body-small" currencySize="x-small" money={totalPrice} />

          {#if bookingStatus}
            <TStatusBadgeCol value={bookingStatus} />
          {:else}
            <TCol width="0" />
          {/if}

          {#if cancellationStatus}
            <TStatusBadgeCol value={cancellationStatus} />
          {:else}
            <TCol width="0" />
          {/if}

          {#if refundStatus}
            <TStatusBadgeCol value={refundStatus} />
          {:else}
            <TCol width="0" />
          {/if}
        </TRow>
      {/each}
    </TBody>
  </Table>
</StandardLayout>

<style>
  :global(.table.orders-table) {
    width: 100%;
    height: 100%;
  }

  a {
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
</style>
