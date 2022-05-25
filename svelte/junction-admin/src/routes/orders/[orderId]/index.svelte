<script lang="ts">
  import { page } from "$app/stores";
  import Crossfader from "$lib/components/ui/crossfader.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { OrderDetailedModel } from "$lib/models/order";
  import Order from "../_components/order.svelte";

  const transitionTimeMs = 150;

  let order: OrderDetailedModel;
  let pending = false;

  $: ({ orderId } = $page.params);
  $: if (orderId) {
    pending = true;
    dependencies.orderService
      .getDetailed(orderId)
      .then((value) => (order = value))
      .catch(() => (order = undefined))
      .finally(() => (pending = false));
  }
</script>

<svelte:head>
  <title>Order management | Order details</title>
</svelte:head>

<div class="order">
  <Crossfader active={pending ? "first" : "second"} {transitionTimeMs}>
    <div class="pending" slot="first">
      <SpinnerIcon />
    </div>

    <svelte:fragment slot="second">
      {#if order}
        <div class="main">
          <Order {order} />
        </div>
      {:else}
        <div class="empty">
          <DocumentNotFoundIcon />
          <span>Order not found</span>
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
