<script lang="ts" context="module">
  export const LOCALE_COOKIE = dev ? "locale" : "__Secure-locale";
</script>

<script lang="ts">
  import i18next from "i18next";
  import { writable } from "svelte/store";
  import { browser, dev } from "$app/environment";
  import { invalidateAll } from "$app/navigation";
  import { setTranslator, type Locale, setTimeFormat } from "$lib/i18n";
  import { ensureDefined } from "$lib/helpers/array";

  export let data;

  const { locale, localeData } = setTranslator(data.locale, data.localeData);

  $: $locale = data.locale;
  $: $localeData = data.localeData;

  const timeFormat = setTimeFormat(writable(data.timeFormat));

  let prevLocale = data.locale;

  $: i18next.changeLanguage(data.locale);
  $: $timeFormat = data.timeFormat;
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
      `SameSite=${dev ? "Lax" : "None"}`,
    ]
      .filter(ensureDefined)
      .join("; ");

    document.cookie = `}`;
    invalidateAll();
  }
</script>

<slot />
