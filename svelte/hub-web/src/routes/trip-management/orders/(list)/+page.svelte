<script lang="ts" context="module">
  function getDepartureDate(order: Order): Date {
    const departureDate = order.bookings
      .flatMap((booking) =>
        booking.detailsList.flatMap((details) => details.legs.flatMap((leg) => leg.departureAt)),
      )
      .sort()[0];

    if (!departureDate) {
      throw new Error("Unknown departure date");
    }

    return departureDate;
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

  function getFilterFunction(
    query: string,
    departureAt: DateRange | undefined,
  ): (order: Order) => boolean {
    const queryLower = query.toLowerCase();

    return (order) => {
      if (departureAt) {
        const date = getZeroTimeDate(getDepartureDate(order));

        if (date < departureAt.from || date > departureAt.to) {
          return false;
        }
      }

      return Boolean(
        order.journey?.reference.toLowerCase().includes(queryLower) ||
          order.passengers.find(
            (item) =>
              item.firstName.toLowerCase().includes(queryLower) ||
              item.lastName.toLowerCase().includes(queryLower),
          ),
      );
    };
  }
</script>

<script lang="ts">
  import PlusIcon from "components/icons/plus-icon.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import Button from "components/ui/button.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";
  import Table from "components/ui/table/table.svelte";
  import { formatAmount } from "formatting/currency";
  import { getOrderStatus } from "integration/junction-mobile-api/schemas/order";
  import type { Order } from "integration/junction-hub-api/schemas/order";
  import type { Price } from "integration/common/schemas/price";
  import type { DateRange } from "models/date-time";
  import routeConfig from "routeConfig";
  import { ensureDefined } from "utils/array";
  import { getZeroTimeDate } from "utils/date-time";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";

  export let data;

  let searchQuery = "";
  let departureAtDateRange: DateRange | undefined = undefined;

  $: orders = data.journeys.data.flatMap((item) => item.orders);

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.journeys.cursor) {
      return { depleted: true };
    }

    const resp = await integrationInstancesClient.hub.journeys.find({
      cursor: data.journeys.cursor,
      limit: 20,
    });

    data.journeys = {
      cursor: resp.cursor,
      data: [...data.journeys.data, ...resp.data],
    };

    return { depleted: !resp.cursor };
  };
</script>

<svelte:head>
  <title>Orders · Trip Management · Junction Hub</title>
</svelte:head>

<StandardLayout pageTitle="Orders" bind:searchQuery filtersActive={Boolean(departureAtDateRange)}>
  <Button size="small" href={routeConfig.routes.tripManagement.routes.book.root} slot="actions">
    New Order
    <PlusIcon />
  </Button>

  <DatePicker
    bind:value={departureAtDateRange}
    label="Departure date"
    range
    placeholder="Date Range"
    slot="filters"
  />

  <Table class="orders-table" {loadMore}>
    <THead>
      <Header>Order Reference</Header>
      <Header>Ticket(s)</Header>
      <Header>Departure Date</Header>
      <Header>Passengers</Header>
      <Header>Total Price</Header>
      <Header>Cancellation Status</Header>
      <Header>Status</Header>
      <Header />
    </THead>

    <TBody>
      {#each orders.filter(getFilterFunction(searchQuery, departureAtDateRange)) as order (order.id)}
        {@const cancellationStatus = getOrderStatus.cancellationStatus(order)}
        {@const status = getOrderStatus.status(order)}
        {@const totalPrice = getTotalPrice(order)}
        {@const hasTickets = Boolean(
          order.bookings.flatMap((item) => item.cancellation).filter(ensureDefined).length,
        )}

        <TRow alternatingBackground={false}>
          <TCol class="typography body-small" width="0">
            <a href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).root}>
              {order.journey?.reference ?? "Unknown"}
            </a>
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
          <TCol class="typography body-small">
            {getDepartureDate(order).toLocaleDateString("sv-SE")}
          </TCol>
          <TCol class="typography body-small">
            <span class="ellipsis typography bold">{getPassengerNames(order).join(", ")}</span>
          </TCol>
          <TCol class="typography body-small">
            <strong>
              {formatAmount(totalPrice)}
            </strong>
            <em class="typography body-xsmall">
              {totalPrice.currency}
            </em>
          </TCol>
          {#if cancellationStatus}
            <TStatusBadgeCol value={cancellationStatus} />
          {:else}
            <TCol width="0" />
          {/if}
          <TStatusBadgeCol value={status} />
          <TActionsCol>
            <button class="action">
              <span>...</span>
            </button>
          </TActionsCol>
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

  a,
  button {
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

  .action {
    padding: 4px;
    background-color: transparent;
    border: 0;
    transform: rotateZ(90deg);
    cursor: pointer;
  }
</style>
