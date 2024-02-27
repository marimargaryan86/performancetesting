<script lang="ts">
  import ArrowsComponent from "$lib/components/arrows-component.svelte";
  import ScrollComponent from "$lib/components/scroll-component.svelte";

  let scroll;
</script>

<!-- <h1>{$t("sentences.comingSoon")}</h1> -->

<ScrollComponent bind:this={scroll}>
  <div class="item"></div>
  <div class="item"></div>
  <div class="item"></div>
  <div class="item"></div>
</ScrollComponent>
<ArrowsComponent on:scroll={scroll.changePosition} />

<style>
  .item {
    min-width: 150px;
    height: 100px;
    background-color: #f2fbff;
  }
</style>
