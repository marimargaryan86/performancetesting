<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import activeLink from "$lib/directives/active-link";
</script>

<div class="places">
  <SubMenu>
    <a href={routeConfig.places.root} use:activeLink>Places</a>

    <a href={routeConfig.places.curatedPlaces} use:activeLink>Curated places</a>
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

  .workspace {
    height: 100%;
  }
</style>
