<script lang="ts">
  import SearchResultTile from "../../components/search-result-tile.svelte";
</script>

<svelte:head>
  <title>Search Results</title>
</svelte:head>

<div class="container">
  <SearchResultTile />
</div>

<style>
  .container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-top: 200px;
  }
</style>
