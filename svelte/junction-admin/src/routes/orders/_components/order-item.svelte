<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import Table from "$lib/components/ui/table.svelte";
  import OverviewIcon from "$lib/icons/overview-icon.svelte";
  import TripIcon from "$lib/icons/trip-icon.svelte";
  import type { OrderItemModel, TripModel } from "$lib/models/order";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";

  type T = $$Generic<OrderItemModel>;

  export let orderItem: T;

  function viewDetails(trip: TripModel): void {
    goto(routeConfig.orders.trip($page.params.orderId, orderItem.id, trip.id));
  }
</script>

<div class="order-item">
  <section class="overview">
    <h2><OverviewIcon /> <span>Overview</span></h2>

    <Table>
      <tr slot="head">
        <td>ID</td>
        <td>Type</td>
        <td>Provider</td>
        <td>Price</td>
        <td>Status</td>
      </tr>

      <tr slot="body">
        <td>{orderItem.id}</td>
        <td>{orderItem.type}</td>
        <td>{orderItem.provider.name}</td>
        <td>{orderItem.price.currency} {orderItem.price.total}</td>
        <td>{orderItem.status}</td>
      </tr>
    </Table>
  </section>

  {#if orderItem.type === "rail" || orderItem.type === "air"}
    <section class="trips">
      <h2><TripIcon /> <span>Trips</span></h2>

      <Table>
        <tr slot="head">
          <td>ID</td>
          <td>Operator</td>
          <td>Departure</td>
          <td>Arrival</td>
          <td>Origin</td>
          <td>Destination</td>
          <td>Segments</td>
        </tr>

        <svelte:fragment slot="body">
          {#each orderItem.trips as trip (trip.id)}
            <tr
              title="Click to view details"
              on:click={() => viewDetails(trip)}
              style:cursor="pointer"
            >
              <td>{trip.id.substring(0, 8)}...</td>
              <td>{trip.operator}</td>
              <td>{trip.departureAt.toLocaleDateString(...utils.fullDateTime)}</td>
              <td>{trip.arrivalAt.toLocaleDateString(...utils.fullDateTime)}</td>
              <td>{trip.origin.name}</td>
              <td>{trip.destination.name}</td>
              <td>{trip.segments.length}</td>
            </tr>
          {/each}
        </svelte:fragment>
      </Table>
    </section>
  {/if}
</div>

<style>
  .order-item {
    padding: 8px;
  }

  section {
    box-shadow: var(--drop-shadow-light);
  }

  h2 {
    user-select: none;
    padding: 8px;
    background-color: var(--color-teal);
  }

  h2 > :global(*) {
    vertical-align: middle;
    color: var(--color-white);
    fill: var(--color-white);
    font-size: 16px;
  }

  section > :global(.table) {
    width: 100%;
  }

  section:not(:last-child) {
    margin-bottom: 16px;
  }
</style>
