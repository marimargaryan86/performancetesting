<script lang="ts">
  import { page } from "$app/stores";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { OrderItemModel } from "$lib/models/order";
  import { fade } from "svelte/transition";
  import OrderItem from "../../_components/order-item.svelte";

  const transitionTimeMs = 150;

  let orderItem: Promise<OrderItemModel> = undefined;
  let pending = false;

  $: ({ orderId, orderItemId } = $page.params);
  $: if (orderId) {
    pending = true;
    orderItem = dependencies.orderService.getOrderItem(orderId, orderItemId);
  }
</script>

<svelte:head>
  <title>Order management | Item details</title>
</svelte:head>

<div class="order-item">
  {#await orderItem}
    <div
      class="pending"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (pending = false)}
    >
      <SpinnerIcon />
    </div>
  {:then orderItem}
    {#if !pending}
      <div
        class="main"
        transition:fade|local={{ duration: transitionTimeMs }}
        on:outroend={() => (pending = true)}
      >
        <OrderItem {orderItem} />
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
