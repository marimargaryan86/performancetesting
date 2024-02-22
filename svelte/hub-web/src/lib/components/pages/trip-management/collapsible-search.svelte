<script lang="ts">
  import Collapsible from "$lib/components/ui/collapsible.svelte";
  import { getTranslator } from "$lib/i18n";
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";

  const t = getTranslator();
</script>

<Collapsible>
  <div class="header" slot="always-visible" let:toggle let:expanded>
    <div class="overview">
      <slot name="overview" />
    </div>

    <button typography="body-medium" weight="bold" on:click={toggle}>
      {$t("actions.modifySearch")}

      <ChevronIcon
        size="16px"
        color="var(--color-main-primary-500)"
        direction={expanded ? "up" : "down"}
      />
    </button>
  </div>

  <div class="search-wrapper" slot="default">
    <slot />
  </div>
</Collapsible>

<style>
  .header > button {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    margin: 0;
    padding: 0;
    color: var(--color-common-light-medium);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .header {
    display: flex;
    gap: 8px;
    max-width: 1152px;
    padding: 16px 24px;
  }

  .header > .overview {
    flex-grow: 1;
  }

  .search-wrapper {
    max-width: 1154px;
    padding: 16px 24px;
    background: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
