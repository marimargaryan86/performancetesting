<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import { getLocale, type Locale } from "i18n";
  import languages from "i18n/lang/languages";
  import { scale } from "svelte/transition";

  export let compact: boolean;
  export let transitionTimeMs: number;

  const locale = getLocale();

  let expanded = false;

  $: selected = languages.find((item) => item.locale === $locale);

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    expanded ? close() : open();
  }

  function select(nextLocale: Locale): void {
    $locale = nextLocale;
    close();
  }
</script>

<div
  class="language-select"
  style:--transition-time="{transitionTimeMs}ms"
  class:compact
  use:clickOutside={close}
>
  <button class="item" on:click={toggle}>
    <span class="icon">{selected?.flag}</span>
    <span class="text" typography="body-medium">{selected?.name}</span>
    <span class="spacer" />
    <ChevronIcon
      direction={expanded ? "up" : "down"}
      color={compact ? "transparent" : "var(--color-common-light-strong)"}
    />
  </button>

  {#if expanded}
    <div class="dialog" transition:scale={{ start: 0.9, duration: 200 }}>
      {#each languages as language}
        <button class="item" on:click={select.bind(select, language.locale)}>
          <span class="icon">{language.flag}</span>
          <span class="text" typography="body-medium">{language.name}</span>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .language-select {
    position: relative;
    width: 100%;
    margin: 0;
    padding: 0;
    text-align: left;
    vertical-align: top;
    background-color: transparent;
    border: 0;
  }

  .item {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
    padding: 10px 8px;
    overflow: hidden;
    color: var(--color-common-light-medium);
    text-align: left;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .item > .icon {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    margin-top: -2px;
    font-size: 18px;
    text-align: center;
  }

  .spacer {
    flex-grow: 1;
  }

  .text {
    transition: opacity var(--transition-time) ease;
  }

  .language-select.compact .item > .text {
    opacity: 0;
  }

  .dialog {
    position: absolute;
    bottom: 100%;
    left: 0;
    width: 100%;
    background-color: var(--color-common-background-light-main);
    border: var(--color-common-line-medium) 1px solid;
    border-radius: 8px;
    transform-origin: bottom left;
  }

  .dialog > .item:not(:last-child) {
    border-bottom: var(--color-common-line-soft) 1px solid;
  }

  .dialog > .item:hover {
    background-color: var(--color-common-background-light-green);
  }
</style>
