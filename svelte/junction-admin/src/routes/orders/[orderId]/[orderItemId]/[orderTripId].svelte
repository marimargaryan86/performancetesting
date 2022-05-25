<script lang="ts">
  import { page } from "$app/stores";
  import Crossfader from "$lib/components/ui/crossfader.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { TripModel } from "$lib/models/order";
  import OrderTrip from "../../_components/order-trip.svelte";

  const transitionTimeMs = 150;

  let orderTrip: TripModel;
  let pending = false;

  $: ({ orderId, orderItemId, orderTripId } = $page.params);
  $: if (orderId) {
    pending = true;
    dependencies.orderService
      .getOrderTrip(orderId, orderItemId, orderTripId)
      .then((value) => (orderTrip = value))
      .catch(() => (orderTrip = undefined))
      .finally(() => (pending = false));
  }
</script>

<svelte:head>
  <title>Order management | Trip details</title>
</svelte:head>

<div class="order-item">
  <Crossfader active={pending ? "first" : "second"}>
    <div class="pending" slot="first">
      <SpinnerIcon />
    </div>

    <svelte:fragment slot="second">
      {#if orderTrip}
        <div class="main">
          <OrderTrip {orderTrip} />
        </div>
      {:else}
        <div class="empty">
          <DocumentNotFoundIcon />
          <span>Order item not found</span>
        </div>
      {/if}
    </svelte:fragment>
  </Crossfader>
</div>

<style>
  .pending,
  .empty {
    text-align: center;
    padding: 8px;
    fill: var(--color-teal);
    user-select: none;
  }

  .pending > :global(*),
  .empty > :global(*) {
    vertical-align: middle;
  }

  .empty > :global(*) {
    fill: var(--color-black);
  }
</style>
