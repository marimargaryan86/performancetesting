<script lang="ts">
  import ArrowsComponent from "$lib/components/arrows-component.svelte";
  import type { Scroll } from "$lib/models/common";

  export let categories: string[] = [];
  export let scroll: Scroll;
  let activeFilter = "All";
</script>

<div class="package-filter-container">
  <div class="package-filters">
    {#each categories as category}
      <button class:active={activeFilter === category} class="category-button">{category}</button>
    {/each}
  </div>
  <div class="scroll-buttons">
    <ArrowsComponent on:scroll={scroll.changePosition} />
  </div>
</div>

<style>
  .package-filter-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    overflow: scroll hidden;
  }

  .package-filters {
    position: relative;
    left: 410px;
    display: flex;
    gap: 16px;
    padding: 8px 0;
  }

  .category-button {
    width: max-content;
    max-width: 175px;
    padding: 12px 24px;
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 500;
    font-size: 14px;
    font-style: normal;
    line-height: normal;
    background: #f6f5f5;
    border: none;
    border-radius: 4px;
  }

  .category-button.active {
    background: rgb(234 113 33 / 0.08);
    border: 1px solid #ea7121;
  }

  @media only screen and (width <= 720px) {
    .package-filter-container {
      overflow: auto;
    }

    .scroll-buttons {
      display: none;
    }
  }
</style>
