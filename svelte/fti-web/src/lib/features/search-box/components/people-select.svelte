<script lang="ts">
  import FaUsers from "svelte-icons/fa/FaUsers.svelte";
  import PassengerSelectionBox from "$lib/features/search-component/passenger-selection-box.svelte";
  import { clickOutside } from "$lib/helpers/click-outside";
  import { getSearchOptionsCtx } from "$lib/stores/search-box.store";
  import { setDropdown, pluralise } from "$lib/helpers/common";

  let dropdown: string = "";
  const clickOutsideHandler = (): string => handleSetDropdown("");
  const handleSetDropdown = (value: string): string => (dropdown = setDropdown(value));
  const searchOptions = getSearchOptionsCtx();
</script>

<div class="search-section people-section" use:clickOutside={clickOutsideHandler}>
  <button class="label people-label" on:click={handleSetDropdown.bind(handleSetDropdown, "people")}>
    <div class="label-container">
      <div class="icon">
        <FaUsers />
      </div>
      <p class="label">Passengers</p>
    </div>
    <p class="desc">
      {$searchOptions.passengers.adults}
      {pluralise($searchOptions.passengers.adults, "adult", "adults")}
      {#if $searchOptions.passengers.children > 0}
        and {$searchOptions.passengers.children}
        {pluralise($searchOptions.passengers.children, "child", "children")}
      {/if}
    </p>
  </button>
  {#if dropdown === "people"}
    <PassengerSelectionBox bind:passengers={$searchOptions.passengers} />
  {/if}
</div>

<style>
  .search-section {
    position: relative;
    display: flex;
    flex-basis: 22.5%;
    gap: 30px;
    align-items: center;
    margin: 0 10px;
    margin-bottom: 12px;
    border-right: 1px solid #1c1c1c;
  }

  .search-section:last-child {
    flex-basis: 10%;
    border-right: none;
  }

  .people-section {
    border: none;
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
  }

  .label-container {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .label {
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
  }

  .label p {
    margin: 0;
    color: var(--text-dark-text);
  }

  .desc {
    margin: 0;
    padding: 6px 0;
    color: var(--text-grey-text, #818181);
    font-weight: 400;
    font-size: 16px;
    line-height: 25px;
    opacity: 0.5;
  }

  button.label:hover {
    cursor: pointer;
  }

  .people-label {
    background: none;
    border: none;
  }

  @media only screen and (width <= 720px) {
    .search-section {
      margin: 0;
      padding: 10px 16px;
      background: #fafafa;
      border: 1px solid #eae9e9;
      border-radius: 4px;
    }

    :global(.dropdown) {
      z-index: 99;
    }
  }
</style>
