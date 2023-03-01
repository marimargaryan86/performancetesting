<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/variables.css";
  import "assets/css/common.css";
  import "assets/css/typography.css";
  import "assets/css/button.css";
  import LoginPage from "components/pages/login-page.svelte";
  import type { LayoutData } from "./$types";

  export let data: LayoutData;
</script>

{#if data.loggedIn}
  <slot />
{:else}
  <LoginPage />
{/if}
