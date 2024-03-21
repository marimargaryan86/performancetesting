<script lang="ts">
  import type { IconTypes } from "$lib/models/common";
  import Icon from "../icon.svelte";

  export let icon: IconTypes = "umbrella";
  export let title: string = "";
</script>

<div class="holiday-type-container">
  <span class="filter-heading">
    <Icon variant={icon} size="16px" color="#01A5C9" />
    {title}
  </span>
  <div class="filter-content">
    <slot />
  </div>
</div>

<style>
  .holiday-type-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 28px 24px;
    background-color: white;
    border-radius: 8px;
  }

  .filter-heading {
    display: flex;
    gap: 8px;
    align-items: center;
    color: var(--meta-neutral-text, #1a1b1c);
    font-weight: 600;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
  }
</style>
