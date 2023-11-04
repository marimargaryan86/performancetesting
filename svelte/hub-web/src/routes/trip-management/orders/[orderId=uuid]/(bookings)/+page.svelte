<script lang="ts">
  import Button from "components/ui/button.svelte";
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import routeConfig from "routeConfig";
  import { getOrigin, getDestination } from "utils/booking";
  import CancellationDialog from "./cancellation-dialog.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";

  export let data;

  let cancellationDialog: CancellationDialog | undefined;

  function cancelBooking(booking: TripBooking): void {
    cancellationDialog?.open(booking);
  }

  function updateOrders(): void {
    data.order = data.order;
  }

  const orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
</script>

<svelte:head>
  <title>
    Bookings · {data.order.journey?.reference ?? "Unknown"} · Orders · Trip Management · Junction Hub
  </title>
</svelte:head>

<CancellationDialog
  bind:this={cancellationDialog}
  orderId={data.order.id}
  passengers={data.order.passengers}
  on:success={updateOrders}
/>

<Table class="bookings-table">
  <THead>
    <Header>Booking</Header>
    <Header />
    <Header>Ticket</Header>
    <Header>Departure Date</Header>
    <Header>Origin</Header>
    <Header>Destination</Header>
    <Header>Total Price</Header>
    <Header>Cancellation Status</Header>
    <Header>Booking status</Header>
    <Header />
  </THead>
  <TBody>
    {#each data.order.bookings as booking, idx}
      {@const origin = getOrigin(booking)}
      {@const destination = getDestination(booking)}

      <TRow>
        <TCol width="0">{idx + 1}</TCol>
        <TCol width="0">
          <a
            href={routeConfig.routes.tripManagement.routes.orders.routes
              .order(data.order.id)
              .routes.booking(booking.id).root}
          >
            View
          </a>
        </TCol>
        <TCol width="0">
          {#if booking.ticketUrls?.length}
            <a
              class="typography body-medium"
              href={orderLink.routes.booking(booking.id).routes.tickets.root}
              download
            >
              Download
            </a>
          {:else}
            <span class="not-available">N/A</span>
          {/if}
        </TCol>
        <TCol>{booking.detailsList[0]?.legs[0]?.departureAt.toLocaleDateString("en-GB")}</TCol>
        <TCol class="typography bold">{origin?.name ?? "Unknown"}</TCol>
        <TCol class="typography bold">{destination?.name ?? "Unknown"}</TCol>
        <TMoneyCol money={booking.price.total} />
        {#if booking.cancellation?.status}
          <TStatusBadgeCol value={booking.cancellation.status} />
        {:else}
          <TCol width="0" />
        {/if}
        <TStatusBadgeCol value={booking.status} />
        <TActionsCol>
          {#if booking.status === "confirmed" && !booking.cancellation?.status}
            <Button
              size="xx-small"
              variant="outline"
              on:click={cancelBooking.bind(cancelBooking, booking)}
            >
              Cancel
            </Button>
          {/if}
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
