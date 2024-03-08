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
    align-items: center;
    overflow-x: scroll;
  }

  .package-filters {
    display: flex;
    flex-basis: 85%;
    gap: 16px;
    min-width: 85%; /* Chrome Fix */
    padding: 30px 0;
  }

  .scroll-buttons {
    flex-basis: 15%;
    min-width: 15% /* Chrome Fix */;
  }

  /* Weird needed  */
  :global(.package-filter-container .scroll-buttons > div.filter-buttons) {
    display: flex;
    gap: 20px;
    justify-content: end;
  }

  .category-button {
    width: max-content;
    max-width: 175px;
    height: 38px;
    padding: 0 34px;
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
      flex-direction: row;
      align-items: center;
      overflow: auto;
    }

    .scroll-buttons {
      display: none;
    }
  }
</style>
