<script lang="ts">
  import Overlay from "$lib/components/overlay.svelte";

  import MainMenu from "$lib/partials/main-menu.svelte";
</script>

<main>
  <MainMenu />

  <slot />
</main>

<Overlay />

<style>
  main {
    display: grid;
    grid-template-rows: 32px 1fr;
    height: 100vh;
  }
</style>
