<script lang="ts" context="module">
  export const LIST_JOURNEYS_LIMIT = 20;
  export const LIST_JOURNEYS_SORT: Parameters<JourneyService["find"]>[0]["sort"] = "-createdAt";

  function getDepartureDateString(order: Order): string {
    const departureLeg = order.bookings
      .flatMap((booking) => booking.detailsList.flatMap((details) => details.legs))
      .sort((a, b) => {
        return a.departureAt.getTime() - b.departureAt.getTime();
      })[0];

    if (!departureLeg) {
      throw new Error("Unknown departure date");
    }

    return departureLeg.departureAt.toLocaleDateString("sv-SE", {
      timeZone: departureLeg.origin.timeZone,
    });
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

  const filters = createQueryStore<FilterOptions, FilterOptionsQuery>(
    (data) => ({
      "createdAt[from]": data.createdAtRange?.from.toLocaleDateString("sv-SE"),
      "createdAt[to]": data.createdAtRange?.to.toLocaleDateString("sv-SE"),
      "departureAt[from]": data.departureAtRange?.from.toLocaleDateString("sv-SE"),
      "departureAt[to]": data.departureAtRange?.to.toLocaleDateString("sv-SE"),
      bookingStatus: data.bookingStatus,
    }),
    (query) => ({
      bookingStatus: bookingStatuses.includes(query.bookingStatus as BookingStatus)
        ? (query.bookingStatus as BookingStatus)
        : undefined,
      createdAtRange: parseDateRange(query["createdAt[from]"], query["createdAt[to]"]),
      departureAtRange: parseDateRange(query["departureAt[from]"], query["departureAt[to]"]),
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
  import { formatAmount } from "formatting/currency";
  import { getOrderStatus } from "integration/common/schemas/order";
  import type { Order } from "integration/junction-hub-api/schemas/order";
  import type { Price } from "integration/common/schemas/price";
  import routeConfig from "routeConfig";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";
  import type JourneyService from "integration/junction-hub-api/services/journey-service";
  import Filters, { type FilterOptions, type FilterOptionsQuery } from "./filters.svelte";
  import { ensureDefined } from "utils/array";
  import { createQueryStore } from "utils/url";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import { parseDateRange } from "utils/date-time";
  import { getPageTitle } from "utils/page-title";

  export let data;

  let searchQuery = "";

  $: orders = data.journeys.data.flatMap((item) => item.orders);

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.journeys.cursor) {
      return { depleted: true };
    }

    const resp = await integrationInstancesClient.hub.journeys.find({
      cursor: data.journeys.cursor,
      limit: LIST_JOURNEYS_LIMIT,
      sort: LIST_JOURNEYS_SORT,
    });

    data.journeys = {
      cursor: resp.cursor,
      data: [...data.journeys.data, ...resp.data],
    };

    return { depleted: !resp.cursor };
  };
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Trip Management", "Orders")}</title>
</svelte:head>

<StandardLayout
  pageTitle="Orders"
  bind:searchQuery
  filtersActive={Boolean(Object.values($filters).find(ensureDefined))}
>
  <Button size="small" href={routeConfig.routes.tripManagement.routes.book.root} slot="actions">
    New Order
    <PlusIcon />
  </Button>

  <Filters slot="filters" bind:filters={$filters} />

  <Table class="orders-table" {loadMore}>
    <THead>
      <Header>Order Reference</Header>
      <Header>Created Date</Header>
      <Header>Ticket(s)</Header>
      <Header>Departure Date</Header>
      <Header>Passengers</Header>
      <Header>Total Price</Header>
      <Header>Booking Status</Header>
      <Header>Cancellation Status</Header>
      <Header>Refund Status</Header>
    </THead>

    <TBody>
      {#each orders as order (order.id)}
        {@const cancellationStatus = getOrderStatus.cancellation(order)}
        {@const refundStatus = getOrderStatus.refund(order)}
        {@const bookingStatus = getOrderStatus.booking(order)}
        {@const totalPrice = getTotalPrice(order)}
        {@const hasTickets = Boolean(order.bookings.flatMap((item) => item.ticketUrls).length)}

        <TRow alternatingBackground={false}>
          <TCol class="typography body-small" width="0">
            <a href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).root}>
              {order.journey?.reference ?? "Unknown"}
            </a>
          </TCol>
          <TCol class="typography body-small" width="0">
            {order.createdAt.toLocaleDateString("sv-SE")}
          </TCol>
          <TCol class="typography body-small" width="0">
            {#if hasTickets}
              <a
                class="typography body-small"
                href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).routes
                  .tickets.root}
                download
              >
                Download
              </a>
            {:else}
              <span class="not-available">N/A</span>
            {/if}
          </TCol>
          <TCol class="typography body-small" width="0">
            {getDepartureDateString(order)}
          </TCol>
          <TCol class="typography body-small bold" maxWidth="240px">
            {getPassengerNames(order).join(", ")}
          </TCol>
          <TCol class="typography body-small" width="0">
            <strong>
              {formatAmount(totalPrice)}
            </strong>
            <em class="typography body-xsmall">
              {totalPrice.currency}
            </em>
          </TCol>

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

  em.body-xsmall {
    color: var(--color-common-light-soft);
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
