<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import { page } from "$app/stores";
  import activeLink from "$lib/directives/active-link";

  $: ({ resellerId } = $page.params);
</script>

<div class="resellers">
  <SubMenu>
    <a href={routeConfig.resellers.root} use:activeLink>List</a>

    {#if resellerId}
      » <a href={routeConfig.resellers.reseller(resellerId)} use:activeLink>Details</a>
    {/if}
  </SubMenu>

  <main class="workspace">
    <slot />
  </main>
</div>

<style>
  .resellers {
    display: grid;
    grid-template-rows: 32px 1fr;
    height: 100%;
  }

  .workspace {
    height: 100%;
  }
</style>
