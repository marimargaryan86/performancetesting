<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import { page } from "$app/stores";

  $: ({ orderId, orderItemId, orderTripId } = $page.params);
</script>

<div class="orders">
  <SubMenu>
    <a href={routeConfig.orders.root} class:active={$page.url.pathname === routeConfig.orders.root}>
      Orders
    </a>

    {#if orderId}
      »
      <a
        href={routeConfig.orders.order(orderId)}
        class:active={$page.url.pathname === routeConfig.orders.order(orderId)}
      >
        Order details
      </a>
    {/if}

    {#if orderItemId}
      »
      <a
        href={routeConfig.orders.item(orderId, orderItemId)}
        class:active={$page.url.pathname === routeConfig.orders.item(orderId, orderItemId)}
      >
        Item details
      </a>
    {/if}

    {#if orderTripId}
      »
      <a
        href={routeConfig.orders.trip(orderId, orderItemId, orderTripId)}
        class:active={$page.url.pathname ===
          routeConfig.orders.trip(orderId, orderItemId, orderTripId)}
      >
        Trip details
      </a>
    {/if}
  </SubMenu>

  <main class="workspace">
    <slot />
  </main>
</div>

<style>
  .orders {
    display: grid;
    grid-template-rows: 32px 1fr;
    height: 100%;
  }

  .orders .active {
    color: var(--color-teal-light);
  }

  .workspace {
    height: 100%;
  }
</style>
