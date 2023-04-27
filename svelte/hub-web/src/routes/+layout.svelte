<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/typography.css";
  import type { LayoutData } from "./$types";
  import Login from "./login.svelte";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";
  import { invalidateAll } from "$app/navigation";
  import { browser } from "$app/environment";

  export let data: LayoutData;

  let logoutTimer: number | undefined = undefined;

  $: setLogoutTimer(data.sessionExpiresAt);

  function setLogoutTimer(timeoutAt?: Date): void {
    if (!(timeoutAt && browser)) {
      return;
    }

    clearTimeout(logoutTimer);

    logoutTimer = setTimeout(
      () => {
        document.cookie = `session-token=; max-age=0; path=/;`;
        invalidateAll();
      },
      timeoutAt.getTime() - new Date().getTime(),
      [],
    );
  }
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
