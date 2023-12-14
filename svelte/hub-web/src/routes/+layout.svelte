<script lang="ts">
  import "assets/css/reset.css";
  import "assets/css/common.css";
  import "assets/css/colors.css";
  import "assets/css/effects.css";
  import "assets/css/typography.css";
  import MainMenu from "components/partials/main-menu/main-menu.svelte";
  import { browser } from "$app/environment";
  import { getTimeDeltaMs } from "utils/date-time";
  import * as Sentry from "@sentry/sveltekit";
  import integrationInstancesClient from "integration-instances-client";
  import { writable } from "svelte/store";
  import { setLocale, setLocaleData, type Locale } from "i18n";
  import { invalidateAll } from "$app/navigation";
  import type { User } from "integration/ory/schemas/authentication";
  import { setUser } from "utils/permissions";

  export let data;

  const user = setUser(writable<User>(data.user));
  const locale = setLocale(writable(data.locale));
  const localeData = setLocaleData(writable(data.localeData));

  let logoutTimer: number | undefined = undefined;
  let prevLocale = data.locale;

  $: $user = data.user as unknown as User;
  $: $localeData = data.localeData;
  $: if (browser && data.sessionExpiresAt) {
    setLogoutTimer(data.sessionExpiresAt);
  }
  $: if ($user) {
    Sentry.setUser({ email: $user.email, id: $user.id });
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

{#if $user}
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
