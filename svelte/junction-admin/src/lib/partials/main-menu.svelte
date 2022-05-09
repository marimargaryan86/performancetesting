<script lang="ts">
  import { page } from "$app/stores";

  import SnowfallLogo from "$lib/icons/snowfall-logo.svelte";
  import routeConfig from "$lib/route-config";
</script>

<header class="main-menu">
  <SnowfallLogo />

  <a
    href={routeConfig.places.root}
    class:active={$page.url.pathname.startsWith(routeConfig.places.root)}
    class="link"
  >
    Places
  </a>

  <a
    href={routeConfig.orders}
    class:active={$page.url.pathname.startsWith(routeConfig.orders)}
    class="link"
  >
    Orders
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

  .link.active {
    color: var(--color-teal-light);
  }
</style>
