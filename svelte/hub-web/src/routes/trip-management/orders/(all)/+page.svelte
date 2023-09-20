<script lang="ts" context="module">
  function getDepartureDate(order: OrderModel): Date {
    const departureDate = order.bookings
      .flatMap((booking) =>
        booking.details.flatMap((details) => details.legs.flatMap((leg) => leg.departureAt)),
      )
      .sort()[0];

    if (!departureDate) {
      throw new Error("Unknown departure date");
    }

    return departureDate;
  }

  function getPassengerNames(order: OrderModel): string[] {
    return order.passengers.map((passenger) => `${passenger.firstName} ${passenger.lastName}`);
  }

  function getTotalPrice(order: OrderModel): PriceModel {
    const prices = order.bookings.flatMap((booking) => booking.price);

    return prices.reduce((prev, curr) => ({
      amount: prev.amount + curr.amount,
      currency: curr.currency,
    }));
  }
</script>

<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import { formatAmount } from "formatting/currency";
  import type { OrderModel } from "integration/junction-mobile-api/schemas/order";
  import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
  import routeConfig from "routeConfig";
  import { ensureDefined } from "utils/array";
  import { downloadTickets } from "utils/booking";

  export let data;
</script>

<svelte:head>
  <title>All · Orders · Trip Management · Junction Hub</title>
</svelte:head>

<Table class="orders-table">
  <THead>
    <Header>Order Reference</Header>
    <Header>Ticket(s)</Header>
    <Header>Departure Date</Header>
    <Header>Passengers</Header>
    <Header>Total Price</Header>
    <Header />
  </THead>

  <TBody>
    {#each data.orders.data as order (order.id)}
      {@const totalPrice = getTotalPrice(order)}
      {@const hasTickets = Boolean(
        order.bookings.map((item) => item.ticketUrl).filter(ensureDefined).length,
      )}

      <TRow alternatingBackground={false}>
        <TCol class="typography body-small" width="0">
          <a href={routeConfig.routes.tripManagement.routes.orders.routes.order(order.id).root}>
            {order.journey?.reference ?? "Unknown"}
          </a>
        </TCol>
        <TCol class="typography body-small" width="0">
          {#if hasTickets}
            <button
              class="typography body-small"
              on:click|preventDefault={downloadTickets.bind(downloadTickets, order.bookings)}
            >
              Download
            </button>
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
        <TActionsCol>
          <button class="action">
            <span>...</span>
          </button>
        </TActionsCol>
      </TRow>
    {/each}
  </TBody>
</Table>

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
