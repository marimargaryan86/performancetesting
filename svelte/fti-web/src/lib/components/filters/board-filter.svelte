<script lang="ts">
  import type { BoardOptions } from "$lib/models/common";
  import Icon from "../icon.svelte";
  import SearchResultFilter from "./search-result-filter.svelte";

  let activeBoard = "board-basis-any";
  let hover = "";
  let boardOptions: BoardOptions[] = [
    {
      title: "Any",
      icon: "board-basis-any",
    },
    {
      title: "Room only",
      icon: "board-basis-room",
    },
    {
      title: "Breakfast",
      icon: "board-basis-breakfast",
    },
    {
      title: "Half board",
      icon: "board-basis-half",
    },
    {
      title: "Full board",
      icon: "board-basis-full",
    },
    {
      title: "All inclusive",
      icon: "board-basis-all",
    },
  ];
</script>

<SearchResultFilter title="Board basis" icon="restaurant">
  <div class="filter-content">
    {#each boardOptions as option}
      <button
        class="filter-item"
        class:active={activeBoard === option.icon}
        class:hover={hover === option.icon}
      >
        <div class="filter-icon">
          <Icon variant={option.icon} size="26px" />
        </div>
        <span class="board-label">{option.title}</span>
        <span class="board-count">(10)</span>
      </button>
    {/each}
  </div>
</SearchResultFilter>

<style>
  .filter-content {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: none;
    border: none;
  }

  .filter-icon {
    display: flex;
    padding: 10px;
    border: 1px solid var(--text-light-stroke);
    border-radius: 8px;
  }

  .filter-item.active .filter-icon {
    background: #f2fbff;
    border-color: #f2fbff;
  }

  .filter-icon :global(.icon) {
    background-color: black;
  }

  .filter-item.active .filter-icon :global(.icon) {
    background-color: var(--colours-primary-blue);
  }

  .filter-item:not(.active):hover .filter-icon {
    border-color: var(--colours-primary-blue);
  }

  .filter-item:hover :global(.icon) {
    background-color: var(--colours-primary-blue);
  }

  .board-label {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 12px;
    line-height: 20px;
    text-align: center;
  }

  .board-count {
    font-weight: 400;
    font-size: 12px;
    line-height: 20px;
  }

  .filter-item.active .board-count {
    color: var(--text-mid);
  }
</style>
