<script lang="ts">
  import type { ResellerSearchData } from "$lib/models/reseller";
  import ResellerResult from "./_components/reseller-result.svelte";
  import ResellerSearch from "./_components/reseller-search.svelte";

  let searchData: ResellerSearchData;
</script>

<svelte:head>
  <title>Reseller management</title>
</svelte:head>

<div class="resellers">
  <ResellerSearch on:search={(e) => (searchData = e.detail)} />

  <div class="main">
    <ResellerResult {searchData} />
  </div>
</div>

<style>
  .resellers {
    display: grid;
    height: 100%;
    grid-template-columns: 280px 1fr max-content;
  }

  .main {
    height: 100%;
    position: relative;
  }

  .main > :global(.reseller-result) {
    height: calc(100% - 8px);
    width: 100%;
    top: 8px;
    position: absolute;
  }
</style>
