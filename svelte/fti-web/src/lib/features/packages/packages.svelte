<script lang="ts">
  import ScrollComponent from "$lib/components/scroll-component.svelte";
  import PackageCard from "./package-card.svelte";
  import PackageFilters from "./package-filters.svelte";
  import type { Package, Scroll } from "$lib/models/common";

  export let categories: string[] = [];
  export let packages: Package[] = [];

  let scroll: Scroll;
  let scrollHtmlElement: HTMLElement;
</script>

<div class="package-section" bind:this={scrollHtmlElement}>
  <h2>Packages you'll love</h2>
  <PackageFilters {categories} bind:scroll />
  <ScrollComponent bind:this={scroll}>
    {#each packages as result}
      <PackageCard holiday={result} />
    {/each}
  </ScrollComponent>
  <button class="show-more-button">See all packages</button>
</div>

<style>
  .package-section {
    display: flex;
    flex-direction: column;
    padding: 0 76px;
  }

  .package-section h2 {
    margin: 0;
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 700;
    font-size: 24px;
    font-style: normal;
    line-height: 44px;
  }

  .show-more-button {
    margin: 40px auto 90px;
    padding: 19px 32px;
    color: #000000;
    font-weight: 600;
    font-size: 16px;
    text-align: center;
    background: none;
    border: 1px solid #000000;
    border-radius: 8px;
  }

  .package-section :global(.scroll-container) {
    gap: 16px;
  }

  @media only screen and (width <= 720px) {
    .package-section {
      padding: 0 16px 32px;
    }

    :global(.scroll-container) {
      margin-top: 24px;
    }
  }
</style>
