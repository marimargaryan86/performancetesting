<script lang="ts">
  import SearchResultFilter from "$lib/components/filters/search-result-filter.svelte";
</script>

<SearchResultFilter title="Hotel Review Score" icon="thumbs-up-down">
  <div class="filter-content">
    <input class="score-slider" type="range" min="1" max="100" value="50" />
  </div>
</SearchResultFilter>

<style>
  .score-slider {
    width: 100%;
    margin-bottom: 14px;
    background: linear-gradient(90deg, #f4c35a 0%, #b4c235 35.33%, #94c126 69.21%, #6fa62b 100%);
    border-radius: 10em;
    outline: none;
    appearance: none;
  }

  input[type="range"]::-webkit-slider-runnable-track {
    height: 4px;
  }

  input[type="range"]::-webkit-slider-thumb {
    position: relative;
    top: 10px;
    width: 12px;
    height: 12px;
    margin-top: -14px;
    background: white;
    border: 2px solid #7cb02a;
    border-radius: 50%;
    cursor: pointer;
    appearance: none;
  }
</style>
