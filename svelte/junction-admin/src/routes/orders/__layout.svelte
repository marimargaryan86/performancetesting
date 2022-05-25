<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import { page } from "$app/stores";
  import activeLink from "$lib/directives/active-link";

  $: ({ orderId, orderItemId, orderTripId } = $page.params);
</script>

<div class="orders">
  <SubMenu>
    <a href={routeConfig.orders.root} use:activeLink>List</a>

    {#if orderId}
      » <a href={routeConfig.orders.order(orderId)} use:activeLink>Order details</a>
    {/if}

    {#if orderItemId}
      » <a href={routeConfig.orders.item(orderId, orderItemId)} use:activeLink>Item details</a>
    {/if}

    {#if orderTripId}
      »
      <a href={routeConfig.orders.trip(orderId, orderItemId, orderTripId)} use:activeLink>
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

  .workspace {
    height: 100%;
  }
</style>
