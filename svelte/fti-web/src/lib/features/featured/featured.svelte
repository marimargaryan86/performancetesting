<script lang="ts">
  import type { FeaturedPackage } from "$lib/models/common";
  import FeaturedCard from "./featured-card.svelte";
  import ScrollComponent from "$lib/components/scroll-component.svelte";
  export let featuredPackages: FeaturedPackage[];

  let scroll;
</script>

<div class="featured-packages-container">
  <ScrollComponent bind:this={scroll}>
    {#each featuredPackages as featuredPackage}
      <FeaturedCard bind:scroll {featuredPackage} />
    {/each}
  </ScrollComponent>
</div>

<style>
  .featured-packages-container {
    display: flex;
    gap: 32px;
    align-items: center;
    padding: 32px;
    overflow-x: scroll;
  }
</style>
