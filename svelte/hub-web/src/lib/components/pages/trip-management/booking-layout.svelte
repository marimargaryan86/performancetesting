<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import { getPageTitle } from "$lib/utils/page-title";
  import { fade } from "svelte/transition";

  export let showActions = false;
  export let pageTitle: string;
  export let pageSubTitle: string;

  const t = getTranslator();
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.book.title"),
      pageTitle,
    )}
  </title>
</svelte:head>

<div class="header">
  <h1 typography="headline-medium" weight="bold">
    {pageSubTitle}
  </h1>
</div>

<div class="content">
  <slot />

  {#if showActions}
    <div class="actions" transition:fade={{ duration: 200 }}>
      <div class="wrapper">
        <slot name="actions" />
      </div>
    </div>
  {/if}
</div>

<style>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    color: var(--color-main-neutral-800);
  }

  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }

  .actions {
    position: relative;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    justify-content: flex-end;
    width: 100%;
    max-width: 1104px;
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }
</style>
