<script lang="ts">
  import { page } from "$app/stores";
  import Crossfader from "$lib/components/ui/crossfader.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { OrderItemModel } from "$lib/models/order";
  import OrderItem from "../../_components/order-item.svelte";

  const transitionTimeMs = 150;

  let orderItem: OrderItemModel;
  let pending = false;

  $: ({ orderId, orderItemId } = $page.params);
  $: if (orderId) {
    pending = true;
    dependencies.orderService
      .getOrderItem(orderId, orderItemId)
      .then((value) => (orderItem = value))
      .catch(() => (orderItem = undefined))
      .finally(() => (pending = false));
  }
</script>

<svelte:head>
  <title>Order management | Item details</title>
</svelte:head>

<div class="order-item">
  <Crossfader active={pending ? "first" : "second"} {transitionTimeMs}>
    <div class="pending" slot="first">
      <SpinnerIcon />
    </div>

    <svelte:fragment slot="second">
      {#if orderItem}
        <div class="main">
          <OrderItem {orderItem} />
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
