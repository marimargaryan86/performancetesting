<script lang="ts">
  import type { BreadCrumb } from "components/page/bread-crumbs.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import routeConfig from "routeConfig";
  import { getDestination, getOrigin } from "utils/booking.js";
  import Passengers from "../../../components/passengers.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import Itinerary from "../../../components/itinerary.svelte";

  export let data;

  let breadCrumbs: BreadCrumb[] = [];

  $: orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
  $: selfLink = orderLink.routes.booking(data.booking.id);
  $: breadCrumbs = [
    { label: "Orders", url: routeConfig.routes.tripManagement.routes.orders.root },
    { label: data.order.journey?.reference ?? "Unknown", url: orderLink.root },
    { label: `Booking ${data.bookingNo}` ?? "Unknown", url: selfLink.root },
  ];
</script>

<svelte:head>
  <title>
    Booking {data.bookingNo} · {data.order.journey?.reference ?? "Unknown"} · Orders · Trip Management
    · Junction Hub
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

  <div class="content">
    <div class="itinerary">
      <h3 class="typography title-large bold">Itinerary</h3>

      <Ticket reference={data.order.journey?.reference} />
    </div>

    <Passengers passengers={data.order.passengers} />

    <Itinerary bookings={[data.booking]} />
  </div>
</StandardLayout>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 48px;
    max-width: 1152px;
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
</style>
