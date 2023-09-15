<script lang="ts" context="module">
  function getOrigin(booking: BookingModel): PointModel | undefined {
    return booking.details[0]?.legs[0]?.origin;
  }

  function getDestination(booking: BookingModel): PointModel | undefined {
    const details = booking.details[booking.details.length - 1];

    return details?.legs[(details?.legs.length ?? 0) - 1]?.destination;
  }
</script>

<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import type { BookingModel } from "integration/junction-mobile-api/schemas/booking";
  import type { PointModel } from "integration/junction-mobile-api/schemas/common";

  export let data;
</script>

<svelte:head>
  <title>
    Bookings · {data.order.journey?.reference ?? "Unknown"} · Orders · Trip Management · Junction Hub
  </title>
</svelte:head>

<Table class="bookings-table">
  <THead>
    <Header>Booking</Header>
    <Header />
    <Header>Ticket</Header>
    <Header>Departure Date</Header>
    <Header>Origin</Header>
    <Header>Destination</Header>
    <Header>Total Price</Header>
    <Header />
  </THead>
  <TBody>
    {#each data.order.bookings as booking, idx}
      {@const origin = getOrigin(booking)}
      {@const destination = getDestination(booking)}
      <TRow>
        <TCol width="0">{idx + 1}</TCol>
        <TCol width="0"><a href="/">View</a></TCol>
        <TCol width="0"><a href="/">Download</a></TCol>
        <TCol>{booking.details[0]?.legs[0]?.departureAt.toLocaleDateString("en-GB")}</TCol>
        <TCol>{origin?.name ?? "Unknown"}</TCol>
        <TCol>{destination?.name ?? "Unknown"}</TCol>
        <TMoneyCol money={booking.price} />
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
  :global(.table.bookings-table) {
    width: 100%;
    height: 100%;
  }

  .action {
    padding: 4px;
    background-color: transparent;
    border: 0;
    transform: rotateZ(90deg);
    cursor: pointer;
  }

  a {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
