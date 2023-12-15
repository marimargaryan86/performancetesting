<script lang="ts">
  import { getLocaleData } from "i18n";

  const i18n = getLocaleData();
</script>

<div>
  {#each $i18n.pages.help.pages.customerService.content as element}
    {#if element.type === "p"}
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html element.html}
    {/if}
  {/each}
</div>

<style>
  div {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  div :global(a) {
    color: var(--color-common-light-text-link);
    text-decoration: none;
  }
</style>
