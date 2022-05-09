<script lang="ts">
  import { page } from "$app/stores";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { TripModel } from "$lib/models/order";
  import { fade } from "svelte/transition";
  import OrderItem from "../../_components/order-item.svelte";
  import OrderTrip from "../../_components/order-trip.svelte";

  const transitionTimeMs = 150;

  let trip: Promise<TripModel> = undefined;
  let pending = false;

  $: ({ orderId, orderItemId, orderTripId } = $page.params);
  $: if (orderId) {
    pending = true;
    trip = dependencies.orderService.getOrderTrip(orderId, orderItemId, orderTripId);
  }
</script>

<svelte:head>
  <title>Order management | Item details</title>
</svelte:head>

<div class="order-item">
  {#await trip}
    <div
      class="pending"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (pending = false)}
    >
      <SpinnerIcon />
    </div>
  {:then orderTrip}
    {#if !pending}
      <div
        class="main"
        transition:fade|local={{ duration: transitionTimeMs }}
        on:outroend={() => (pending = true)}
      >
        <OrderTrip {orderTrip} />
      </div>
    {/if}
  {:catch}
    {#if !pending}
      <div
        class="empty"
        transition:fade|local={{ duration: transitionTimeMs }}
        on:outroend={() => (pending = true)}
      >
        <DocumentNotFoundIcon />
        <span>Order item not found</span>
      </div>
    {/if}
  {/await}
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
