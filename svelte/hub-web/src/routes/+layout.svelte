<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/common.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/typography.css";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";
  import { browser } from "$app/environment";
  import userStore from "stores/user-store";
  import { getTimeDeltaMs } from "utils/date-time";
  import * as Sentry from "@sentry/sveltekit";
  import integrationInstancesClient from "integration-instances-client";
  import { writable } from "svelte/store";
  import { setLocale, setLocaleData, type Locale } from "i18n";
  import { invalidateAll } from "$app/navigation";

  export let data;

  const locale = writable(data.locale);
  const localeData = writable(data.localeData);
  setLocale(locale);
  setLocaleData(localeData);

  let logoutTimer: number | undefined = undefined;
  let prevLocale = data.locale;

  $: $localeData = data.localeData;
  $: if (browser && data.sessionExpiresAt) {
    setLogoutTimer(data.sessionExpiresAt);
  }
  $: if (data.user) {
    Sentry.setUser({ email: data.user.email, id: data.user.id });
    $userStore = data.user;
  } else {
    Sentry.setUser(null);
  }
  $: if (browser && prevLocale !== $locale) {
    prevLocale = $locale;
    updateLocaleCookie($locale);
  }

  function updateLocaleCookie(nextLocale: Locale): void {
    document.cookie = `locale=${nextLocale}; Path=/; MaxAge=31536000; SameSite=Lax`;
    invalidateAll();
  }

  function setLogoutTimer(timeoutAt: Date): void {
    window.clearTimeout(logoutTimer);

    logoutTimer = window.setTimeout(
      integrationInstancesClient.ory.auth.logout,
      getTimeDeltaMs(timeoutAt, new Date()),
    );
  }
</script>

{#if data.user}
  <div class="workspace">
    <MainMenu />

    <main>
      <slot />
    </main>
  </div>
{:else if data.authenticated}
  <main>
    <slot />
  </main>
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
