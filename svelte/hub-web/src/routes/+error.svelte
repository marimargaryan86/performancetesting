<script lang="ts">
  import { page } from "$app/stores";
  import { getLocaleData } from "~/i18n";
  import { getPageTitle } from "~/utils/page-title";

  const i18n = getLocaleData();
</script>

<svelte:head>
  <title>{getPageTitle($i18n.title, $i18n.words.error)}</title>
</svelte:head>

<main>
  {#if $page.status === 500}
    <h1 typography="headline-medium">{$i18n.sentences.oopsSomethingWentWrong}</h1>
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
