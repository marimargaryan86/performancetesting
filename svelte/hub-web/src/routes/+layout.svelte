<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/common.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/typography.css";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";
  import { browser } from "$app/environment";
  import routeConfig from "routeConfig";
  import { callAction } from "utils/common";
  import { getTimeDeltaMs } from "utils/date-time.js";

  export let data;

  let logoutTimer: number | undefined = undefined;

  $: if (browser && data.user) {
    setLogoutTimer(data.user.sessionExpiresAt);
  }

  function setLogoutTimer(timeoutAt: Date): void {
    window.clearTimeout(logoutTimer);

    logoutTimer = window.setTimeout(callAction, getTimeDeltaMs(timeoutAt, new Date()), {
      action: `${routeConfig.login}?/logout`,
    });
  }
</script>

{#if data.user}
  <div class="workspace">
    <MainMenu user={data.user.data} />

    <main>
      <slot />
    </main>
  </div>
{:else}
  <slot />
{/if}

<style>
  .workspace {
    display: grid;
    grid-template-columns: max-content 1fr;
    height: 100vh;
  }

  main {
    display: flex;
    flex-flow: column;
    height: 100vh;
    overflow: auto;
    background-color: #ffffff;
  }
</style>
