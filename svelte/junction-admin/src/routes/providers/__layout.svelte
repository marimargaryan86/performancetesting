<script lang="ts">
  import SubMenu from "$lib/partials/sub-menu.svelte";
  import routeConfig from "$lib/route-config";
  import { page } from "$app/stores";
  import activeLink from "$lib/directives/active-link";

  $: ({ providerId } = $page.params);
</script>

<div class="providers">
  <SubMenu>
    <a href={routeConfig.providers.root} use:activeLink>List</a>

    {#if providerId}
      » <a href={routeConfig.providers.provider(providerId)} use:activeLink>Details</a>
    {/if}
  </SubMenu>

  <main class="workspace">
    <slot />
  </main>
</div>

<style>
  .providers {
    display: grid;
    grid-template-rows: 32px 1fr;
    height: 100%;
  }

  .workspace {
    height: 100%;
  }
</style>
