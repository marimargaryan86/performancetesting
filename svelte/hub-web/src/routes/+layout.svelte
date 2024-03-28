<script lang="ts" context="module">
  export const LOCALE_COOKIE = dev ? "locale" : "__Secure-locale";
</script>

<script lang="ts">
  import MainMenu from "$lib/components/partials/main-menu/main-menu.svelte";
  import { browser, dev } from "$app/environment";
  import { getTimeDeltaMs } from "$lib/utils/date-time";
  import * as Sentry from "@sentry/sveltekit";
  import Smartlook from "smartlook-client";
  import integrationInstancesClient from "~/integration-instances-client";
  import { writable } from "svelte/store";
  import { setTranslator, type Locale, setTimeFormat } from "$lib/i18n";
  import { invalidateAll } from "$app/navigation";
  import type * as OrySchemas from "~/integration/ory/schemas";
  import { setUser } from "$lib/utils/permissions";
  import { setQueryStore } from "$lib/stores/query-store";
  import { page } from "$app/stores";
  import i18next from "i18next";
  import { Feature, getFeatureTools, setFeatures } from "$lib/utils/feature-flags";
  import DevTools from "$lib/components/partials/dev-tools.svelte";
  import { ensureDefined } from "$lib/utils/array";
  import Toaster from "$lib/components/ui/toaster.svelte";

  export let data;

  const { locale, localeData } = setTranslator(data.locale, data.localeData);

  $: $locale = data.locale;
  $: $localeData = data.localeData;

  const features = setFeatures(data.features);
  const featureTools = getFeatureTools();
  const queryStore = setQueryStore($page.url.searchParams);
  const user = setUser(writable<OrySchemas.User>(data.user));
  const timeFormat = setTimeFormat(writable(data.timeFormat));

  let logoutTimer: number | undefined = undefined;
  let prevLocale = data.locale;

  $: i18next.changeLanguage(data.locale);
  $: $features = data.features;
  $: $queryStore = Object.fromEntries($page.url.searchParams);
  $: $timeFormat = data.timeFormat;
  $: $user = data.user as unknown as OrySchemas.User;
  $: if (browser && data.sessionExpiresAt) {
    setLogoutTimer(data.sessionExpiresAt);
  }
  $: if ($user) {
    if (Smartlook.initialized()) {
      Smartlook.identify($user.id, { email: $user.email, role: $user.role });
    }
    Sentry.setUser({ email: $user.email, id: $user.id });
  } else {
    Sentry.setUser(null);
  }
  $: if (browser && prevLocale !== $locale) {
    prevLocale = $locale;
    updateLocaleCookie($locale);
  }

  function updateLocaleCookie(nextLocale: Locale): void {
    document.cookie = [
      `${LOCALE_COOKIE}=${nextLocale}`,
      dev ? undefined : `Secure`,
      "Path=/",
      "MaxAge=31536000",
      `SameSite=${dev ? "lax" : "strict"}`,
    ]
      .filter(ensureDefined)
      .join("; ");

    document.cookie = `}`;
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

{#if $page.url.pathname.startsWith("/adapter")}
  <slot />
{:else if $user}
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

{#if $featureTools.hasFeature(Feature.DEV_TOOLS)}
  <DevTools />
{/if}

<Toaster />

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
