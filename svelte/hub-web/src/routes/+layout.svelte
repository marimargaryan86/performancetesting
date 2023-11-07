<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/common.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/typography.css";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";
  import { browser } from "$app/environment";
  import routeConfig from "routeConfig";
  import userStore from "stores/user-store";
  import { getTimeDeltaMs } from "utils/date-time";
  import * as Sentry from "@sentry/sveltekit";
  import integrationInstancesClient from "integration-instances-client";
  import { goto } from "$app/navigation";

  export let data;

  let logoutTimer: number | undefined = undefined;

  $: if (browser && data.sessionExpiresAt) {
    setLogoutTimer(data.sessionExpiresAt);
  }
  $: if (data.user) {
    Sentry.setUser({ email: data.user.email, id: data.user.id });
    $userStore = data.user;
  } else {
    Sentry.setUser(null);
  }

  function setLogoutTimer(timeoutAt: Date): void {
    window.clearTimeout(logoutTimer);

    logoutTimer = window.setTimeout(async () => {
      await integrationInstancesClient.auth.signOut();
      await goto(routeConfig.routes.login.root, { invalidateAll: true });
    }, getTimeDeltaMs(timeoutAt, new Date()));
  }
</script>

{#if data.user}
  <div class="workspace">
    <MainMenu />

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
