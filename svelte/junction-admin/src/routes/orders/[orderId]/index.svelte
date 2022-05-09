<script lang="ts">
  import { page } from "$app/stores";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { OrderDetailedModel } from "$lib/models/order";
  import { fade } from "svelte/transition";
  import Order from "../_components/order.svelte";

  const transitionTimeMs = 150;

  let order: Promise<OrderDetailedModel> = undefined;
  let pending = false;

  $: ({ orderId } = $page.params);
  $: if (orderId) {
    pending = true;
    order = dependencies.orderService.getDetailed(orderId);
  }
</script>

<svelte:head>
  <title>Order management | Order details</title>
</svelte:head>

<div class="order">
  {#await order}
    <div
      class="pending"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (pending = false)}
    >
      <SpinnerIcon />
    </div>
  {:then order}
    {#if !pending}
      <div
        class="main"
        transition:fade|local={{ duration: transitionTimeMs }}
        on:outroend={() => (pending = true)}
      >
        <Order {order} />
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
        <span>Order not found</span>
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
