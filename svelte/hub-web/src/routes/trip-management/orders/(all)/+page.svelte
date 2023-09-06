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

  export let data;
</script>

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

      <TRow alternatingBackground={false}>
        <TCol class="typography body-small">
          <span class="highlight">
            {order.journey?.reference ?? "Unknown"}
          </span>
        </TCol>
        <TCol class="typography body-small">
          <a href="/">Download</a>
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

  .highlight,
  a {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }

  .action {
    padding: 4px;
    background-color: transparent;
    border: 0;
    transform: rotateZ(90deg);
    cursor: pointer;
  }
</style>
