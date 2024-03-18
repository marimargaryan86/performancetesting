<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import Icon from "./icon.svelte";

  const dispatch = createEventDispatcher<{ scroll: boolean }>();
  export const setContainerScroll = (item: boolean): void => {
    dispatch("scroll", item);
  };
</script>

<div class="filter-buttons">
  <button class="filter-button" on:click={setContainerScroll.bind(setContainerScroll, false)}>
    <div class="icon">
      <img src="/icons/chevron-left.svg" alt="Chevron Left" />
      <Icon variant="chevron-left" />
    </div>
  </button>
  <button class="filter-button" on:click={setContainerScroll.bind(setContainerScroll, true)}>
    <div class="icon">
      <img src="/icons/chevron-right.svg" alt="Chevron Right" />
    </div>
  </button>
</div>

<style>
  .filter-buttons {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .filter-button {
    height: 32px;
    padding: 0;
    background: none;
    border: 1px solid black;
    border-radius: 50%;
  }

  .filter-button:hover {
    cursor: pointer;
  }

  .filter-button .icon {
    position: relative;
    width: 30px;
    height: 30px;
  }

  .filter-button .icon img {
    position: absolute;
    left: 0;
    width: 18px;
    height: 28px;
    padding: 2px 6px;
  }
</style>
