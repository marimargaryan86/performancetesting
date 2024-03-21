<script lang="ts">
  import SearchResultFilter from "$lib/components/filters/search-result-filter.svelte";
  import Icon from "../icon.svelte";

  export let selectedItems: string[] = [];
  export let items = ["Kids Club", "Wellness centre", "Direct beach access", "Pool", "Gym", "WiFi"];
</script>

<SearchResultFilter title="Facilities" icon="hot-tub">
  <div class="filter-content">
    {#each items as item}
      <div class="filter-item">
        <input
          class="filter-checkbox"
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
  <button class="expand">
    <span>Show all</span>
    <Icon variant="chevron-down" size="20px" color="#01a5c9" />
  </button>
</SearchResultFilter>

<style>
  .filter-item {
    display: flex;
    gap: 12px;
  }

  .filter-item span {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 15px;
    line-height: 24px;
  }

  .expand {
    display: flex;
    gap: 4px;
    align-items: center;
    margin-top: 8px;
    background: none;
    border: none;
  }

  .expand:hover {
    text-decoration: none;
  }

  .expand span {
    color: var(--text-secondary-blue, #01a5c9);
    font-weight: 600;
    font-size: 14px;
    font-style: normal;
    line-height: normal;
    text-align: right;
  }

  .expand :global(.icon) {
    margin-top: 4px;
  }
</style>
