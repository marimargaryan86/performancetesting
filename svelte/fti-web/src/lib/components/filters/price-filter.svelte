<script lang="ts">
  import SearchResultFilter from "$lib/components/filters/search-result-filter.svelte";
  import SliderRange from "$lib/components/slider-range.svelte";
</script>

<SearchResultFilter title="Price" icon="restaurant">
  <div class="filter-content">
    <SliderRange />
  </div>
</SearchResultFilter>

<style>
  .filter-content {
    position: relative;
    min-width: 200px;
  }
</style>
