<script lang="ts">
  import { getTranslator } from "$lib/i18n";

  const t = getTranslator();
</script>

<div>
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
  {@html $t("pages.help.pages.termsAndConditions.content")}
</div>

<style>
  div {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  div :global(h2) {
    margin-bottom: -8px;
    color: var(--color-main-primary-900);
  }
</style>
