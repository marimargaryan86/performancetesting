<script lang="ts">
  import type { BreadCrumb } from "components/page/bread-crumbs.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import routeConfig from "routeConfig";
  import { getDestination, getOrigin } from "utils/booking";
  import Passengers from "../../../components/passengers.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import Itinerary from "../../../components/itinerary.svelte";
  import StatusBadge from "components/ui/status-badge.svelte";
  import { permitted } from "utils/permissions";
  import userStore from "stores/user-store";
  import Admin from "./admin.svelte";

  export let data;

  let breadCrumbs: BreadCrumb[] = [];

  $: order = data.booking.order;
  $: reservationNo = data.booking.operatorBookingReferences.length
    ? data.booking.operatorBookingReferences.join(", ")
    : undefined;
  $: orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.booking.orderId);
  $: selfLink = orderLink.routes.booking(data.booking.id);
  $: breadCrumbs = [
    { label: "Orders", url: routeConfig.routes.tripManagement.routes.orders.root },
    { label: order?.journey?.reference ?? "Unknown", url: orderLink.root },
    { label: `Booking ${data.bookingNo}` ?? "Unknown", url: selfLink.root },
  ];
  $: transactionsPermitted = permitted($userStore, "transaction", "view");
</script>

<svelte:head>
  <title>
    Booking {data.bookingNo} · {order?.journey?.reference ?? "Unknown"} · Orders · Trip Management ·
    Junction Hub
  </title>
</svelte:head>

<StandardLayout {breadCrumbs}>
  <svelte:fragment slot="page-title">
    Booking {data.bookingNo}:
    <span class="typography title-large bold">
      {getOrigin(data.booking)?.name ?? "Unknown"}
      to
      {getDestination(data.booking)?.name ?? "Unknown"}
    </span>
  </svelte:fragment>

  <div class="content" style:--grid-columns={transactionsPermitted ? "1fr 1fr" : "1fr"}>
    <div class="booking">
      <div class="itinerary">
        <h3 class="typography title-large bold">Itinerary</h3>

        <Ticket identifier={reservationNo} title="Reservation number" />

        <div class="statuses">
          <div class="status typography body-small bold">
            Booking status
            <StatusBadge value={data.booking.status} />
          </div>

          {#if data.booking.cancellation?.status}
            <div class="status typography body-small bold">
              Cancellation status
              <StatusBadge value={data.booking.cancellation.status} />
            </div>
          {/if}
        </div>
      </div>

      {#if order}
        <Passengers passengers={order.passengers} />
      {/if}

      <Itinerary bookings={[data.booking]} />
    </div>

    {#if transactionsPermitted}
      <Admin bind:booking={data.booking} />
    {/if}
  </div>
</StandardLayout>

<style>
  .content {
    display: grid;
    grid-template-columns: var(--grid-columns);
    gap: 24px;
    align-items: flex-start;
    max-width: 1152px;
  }

  .booking {
    display: flex;
    flex-flow: column;
    gap: 48px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .itinerary {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }

  .statuses {
    display: flex;
    gap: 8px;
    width: 100%;
  }

  .status {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 8px;
    align-items: flex-start;
  }
</style>
