<script lang="ts">
  import activeLink from "$lib/directives/active-link";
  import OrderItemsIcon from "$lib/icons/order-items-icon.svelte";
  import OverviewIcon from "$lib/icons/overview-icon.svelte";
  import PlaceIcon from "$lib/icons/place-icon.svelte";
  import ResellerIcon from "$lib/icons/reseller-icon.svelte";
  import SnowfallLogo from "$lib/icons/snowfall-logo.svelte";
  import routeConfig from "$lib/route-config";
</script>

<header class="main-menu">
  <SnowfallLogo />

  <a href={routeConfig.places.root} use:activeLink={false} class="link">
    <PlaceIcon />
    <span>Places</span>
  </a>

  <a href={routeConfig.orders.root} use:activeLink={false} class="link">
    <OverviewIcon />
    <span>Orders</span>
  </a>

  <a href={routeConfig.resellers.root} use:activeLink={false} class="link">
    <ResellerIcon />
    <span>Resellers</span>
  </a>

  <a href={routeConfig.providers.root} use:activeLink={false} class="link stroked">
    <OrderItemsIcon />
    <span>Providers</span>
  </a>
</header>

<style>
  .main-menu {
    display: flex;
    align-items: center;
    height: 32px;
    background: var(--color-black);
    box-shadow: var(--drop-shadow);
    user-select: none;
  }

  .main-menu > :global(.snowfall-logo) {
    margin: 0 8px;
  }

  .link {
    text-decoration: none;
    display: block;
    font-weight: 600;
    font-size: 12px;
    color: var(--color-white);
    margin: 0px 8px;
  }

  header :global(.link.active) {
    color: var(--color-teal-light);
  }

  .link > span {
    vertical-align: middle;
  }

  .link > :global(svg) {
    fill: var(--color-white);
    height: 12px;
    width: 12px;
    vertical-align: middle;
  }

  .link.stroked > :global(svg) {
    stroke: var(--color-white);
  }

  header :global(.link.active) > :global(svg) {
    fill: var(--color-teal-light);
  }
</style>
