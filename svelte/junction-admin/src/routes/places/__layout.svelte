<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import { page } from "$app/stores";
</script>

<div class="places">
  <SubMenu>
    <a href={routeConfig.places.root} class:active={$page.url.pathname === routeConfig.places.root}>
      Places
    </a>

    <a
      href={routeConfig.places.curated}
      class:active={$page.url.pathname === routeConfig.places.curated}
    >
      Curated places
    </a>
  </SubMenu>

  <main class="workspace">
    <slot />
  </main>
</div>

<style>
  .places {
    display: grid;
    grid-template-rows: 32px 1fr;
    height: 100%;
  }

  .places .active {
    color: var(--color-teal-light);
  }

  .workspace {
    height: 100%;
  }
</style>
