<script lang="ts">
  import SearchResultFilter from "$lib/components/filters/search-result-filter.svelte";
  import Icon from "../icon.svelte";

  export let selectedItems: string[] = [];
  export let items = [2, 24, 24, 24, 24];
</script>

<SearchResultFilter title="Hotel Rating" icon="star">
  <div class="filter-content">
    {#each items as item, i}
      <div class="filter-item">
        <input
          type="checkbox"
          id="all-inclusive"
          name="all-inclusive"
          bind:group={selectedItems}
          value={item}
        />
        <span class="stars">
          {#each Array(5 - i) as _}
            <div class="star-container" id={_}>
              <Icon variant="star" size="16px" color="#FFD700" />
            </div>
          {/each}
        </span>
        <span class="count">(24)</span>
      </div>
    {/each}
  </div>
</SearchResultFilter>

<style>
  .filter-item {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .stars {
    display: flex;
    flex-grow: 1;
    align-items: center;
  }

  .count {
    padding-left: 25px;
    color: var(--text-mid, #818181);
    font-weight: 400;
    font-size: 14px;
    line-height: 24px;
    text-align: right;
  }
</style>
