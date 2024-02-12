<script lang="ts">
  import { page } from "$app/stores";
  import { getTranslator } from "$lib/i18n";
  import { getPageTitle } from "$lib/utils/page-title";

  const t = getTranslator();
</script>

<svelte:head>
  <title>{getPageTitle($t("title"), $t("words.error"))}</title>
</svelte:head>

<main>
  {#if $page.status === 500}
    <h1 typography="headline-medium">{$t("sentences.oopsSomethingWentWrong")}</h1>
  {:else}
    <h1 typography="headline-medium">{$page.error?.message}</h1>
  {/if}
</main>

<style>
  main {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
  }
</style>
