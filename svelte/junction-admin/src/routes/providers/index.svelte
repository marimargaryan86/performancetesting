<script lang="ts">
  import type { ProviderSearchData } from "$lib/models/provider";
  import ProviderResult from "./_components/provider-result.svelte";
  import ProviderSearch from "./_components/provider-search.svelte";

  let searchData: ProviderSearchData;
</script>

<svelte:head>
  <title>Provider management</title>
</svelte:head>

<div class="providers">
  <ProviderSearch on:search={(e) => (searchData = e.detail)} />

  <div class="main">
    <ProviderResult {searchData} />
  </div>
</div>

<style>
  .providers {
    display: grid;
    height: 100%;
    grid-template-columns: 280px 1fr max-content;
  }

  .main {
    height: 100%;
    position: relative;
  }

  .main > :global(.provider-result) {
    height: calc(100% - 8px);
    width: 100%;
    top: 8px;
    position: absolute;
  }
</style>
