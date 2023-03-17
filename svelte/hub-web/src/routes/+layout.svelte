<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/common.css";
  import "assets/css/layout.css";
  import "assets/css/typography.css";
  import "assets/css/table.css";
  import type { LayoutData } from "./$types";
  import Login from "./login.svelte";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";

  export let data: LayoutData;
</script>

{#if data.user}
  <div class="workspace">
    <MainMenu user={data.user} />

    <main>
      <slot />
    </main>
  </div>
{:else}
  <Login />
{/if}

<style>
  .workspace {
    display: grid;
    grid-template-columns: max-content 1fr;
  }

  main {
    padding: 16px 16px 0;
    overflow-y: auto;
    background-image: linear-gradient(284.73deg, #9dc6bf 0%, #eaf8ec 100%);
  }
</style>
