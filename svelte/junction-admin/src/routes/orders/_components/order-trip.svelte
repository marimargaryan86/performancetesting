<script lang="ts">
  import Table from "$lib/components/ui/table.svelte";
  import OverviewIcon from "$lib/icons/overview-icon.svelte";
  import TripIcon from "$lib/icons/trip-icon.svelte";
  import type { TripModel } from "$lib/models/order";
  import utils from "$lib/utils";

  export let orderTrip: TripModel;
</script>

<div class="order-trip">
  <section class="overview">
    <h2><OverviewIcon /> <span>Overview</span></h2>

    <Table>
      <tr slot="head">
        <td>ID</td>
        <td>Operator</td>
        <td>Origin</td>
        <td>Destination</td>
        <td>Departure</td>
        <td>Arrival</td>
      </tr>

      <tr slot="body">
        <td>{orderTrip.id}</td>
        <td>{orderTrip.operator}</td>
        <td>{orderTrip.origin.name}</td>
        <td>{orderTrip.destination.name}</td>
        <td>{orderTrip.departureAt.toLocaleDateString(...utils.fullDateTime)}</td>
        <td>{orderTrip.arrivalAt.toLocaleDateString(...utils.fullDateTime)}</td>
      </tr>
    </Table>
  </section>

  <section class="segments">
    <h2><TripIcon /> <span>Segments</span></h2>

    <Table>
      <tr slot="head">
        <td>Origin</td>
        <td>Destination</td>
        <td>Departure</td>
        <td>Arrival</td>
      </tr>

      <svelte:fragment slot="body">
        {#each orderTrip.segments as segment}
          <tr>
            <td>{segment.origin.name}</td>
            <td>{segment.destination.name}</td>
            <td>{segment.departureAt.toLocaleDateString(...utils.fullDateTime)}</td>
            <td>{segment.arrivalAt.toLocaleDateString(...utils.fullDateTime)}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  </section>
</div>

<style>
  .order-trip {
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
