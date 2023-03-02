<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/variables.css";
  import "assets/css/common.css";
  import "assets/css/typography.css";
  import "assets/css/button.css";
  import LoginPage from "components/pages/login-page.svelte";
  import type { LayoutData } from "./$types";
  import MainNavBar from "components/partials/main-nav-bar/main-nav-bar.svelte";

  export let data: LayoutData;
</script>

{#if data.loggedIn}
  <main>
    <MainNavBar />

    <slot />
  </main>
{:else}
  <LoginPage />
{/if}

<style>
  main {
    display: grid;
    grid-template-columns: max-content 1fr;
    height: 100vh;
  }
</style>
