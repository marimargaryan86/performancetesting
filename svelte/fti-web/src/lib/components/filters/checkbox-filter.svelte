<script lang="ts">
  import SearchResultFilter from "$lib/components/filters/search-result-filter.svelte";

  export let selectedItems: string[] = [];
  export let items = ["All inclusive", "Family", "XYZ"];
</script>

<SearchResultFilter title="Holiday Type" icon="umbrella">
  <div class="filter-content">
    {#each items as item}
      <div class="filter-item">
        <input
          type="checkbox"
          id="all-inclusive"
          name="all-inclusive"
          bind:group={selectedItems}
          value={item}
        />
        <span>{item}</span>
      </div>
    {/each}
  </div>
  <div class="expand">Expand items</div>
</SearchResultFilter>
