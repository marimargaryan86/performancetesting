<script lang="ts">
  import { setTranslator, type Locale } from "$lib/i18n";
  import { invalidateAll } from "$app/navigation";
  import { browser } from "$app/environment";
  import Navigation from "../navigation.svelte";

  export let data;

  const { locale, localeData } = setTranslator(data.locale, data.localeData);

  $: $locale = data.locale;
  $: $localeData = data.localeData;

  let prevLocale = data.locale;

  $: if (browser && prevLocale !== $locale) {
    prevLocale = $locale;
    updateLocaleCookie($locale);
  }

  function updateLocaleCookie(nextLocale: Locale): void {
    document.cookie = `locale=${nextLocale}; Path=/; MaxAge=31536000; SameSite=lax;`;
    invalidateAll();
  }
</script>

<svelte:head>
  <title>BigXtra - immer etwas neues</title>
</svelte:head>

<div class="app">
  <Navigation />

  <main>
    <slot />
  </main>

  <footer>
    <p>
      Something broken? <a href="mailto:nathan.l@snowfalltravel.com">Email Nathan</a> I'll see what I
      can do to fix it :)
    </p>
  </footer>
</div>

<style>
  * {
    font-family: "Plus Jakarta Sans", sans-serif;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: #eaeaea;
  }

  /* main {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 1rem;
    width: 100%;
    max-width: 64rem;
    margin: 0 auto;
    box-sizing: border-box;
  } */

  main {
    position: relative;
    left: 0;
    width: 100%;
  }

  footer {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px;
  }

  footer a {
    font-weight: 700;
  }

  @media (width >= 480px) {
    footer {
      padding: 12px 0;
    }
  }
</style>
