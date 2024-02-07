<script lang="ts">
  import MainMenu from "~/components/partials/main-menu/main-menu.svelte";
  import { browser } from "$app/environment";
  import { getTimeDeltaMs } from "~/utils/date-time";
  import * as Sentry from "@sentry/sveltekit";
  import integrationInstancesClient from "~/integration-instances-client";
  import { writable } from "svelte/store";
  import { setTranslator, type Locale, setTimeFormat } from "~/i18n";
  import { invalidateAll } from "$app/navigation";
  import type { User } from "~/integration/ory/schemas/authentication";
  import { setUser } from "~/utils/permissions";
  import { setQueryStore } from "~/stores/query-store";
  import { page } from "$app/stores";
  import i18next from "i18next";

  export let data;

  const { locale, localeData } = setTranslator(data.locale, data.localeData);

  $: $locale = data.locale;
  $: $localeData = data.localeData;

  const queryStore = setQueryStore($page.url.searchParams);
  const user = setUser(writable<User>(data.user));
  const timeFormat = setTimeFormat(writable(data.timeFormat));

  let logoutTimer: number | undefined = undefined;
  let prevLocale = data.locale;

  $: i18next.changeLanguage(data.locale);
  $: $queryStore = Object.fromEntries($page.url.searchParams);
  $: $timeFormat = data.timeFormat;
  $: $user = data.user as unknown as User;
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
