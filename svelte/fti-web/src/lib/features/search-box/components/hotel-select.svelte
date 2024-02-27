<script lang="ts">
  import FaUsers from "svelte-icons/fa/FaUsers.svelte";
  import { getSearchOptionsCtx } from "$lib/stores/search-box.store";
  import RoomsSelect from "$lib/features/search-component/rooms-select.svelte";
  import { setDropdown } from "$lib/helpers/common";
  import { clickOutside } from "$lib/helpers/click-outside";

  let dropdown: string = "";
  const clickOutsideHandler = (): string => handleSetDropdown("");
  const handleSetDropdown = (value: string): string => (dropdown = setDropdown(value));
  const searchOptions = getSearchOptionsCtx();
</script>

<div class="search-section hotel-section" use:clickOutside={clickOutsideHandler}>
  <button class="label hotel-label" on:click={handleSetDropdown.bind(handleSetDropdown, "hotels")}>
    <div class="label-container">
      <div class="icon">
        <FaUsers />
      </div>
      <p class="label">Rooms & Guests</p>
    </div>
    <p class="desc">Select Guests</p>
  </button>
  {#if dropdown === "hotels"}
    <RoomsSelect bind:rooms={$searchOptions.rooms} />
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

  .label-container {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .label p {
    margin: 0;
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
  }

  .desc {
    color: #1c1c1c;
    color: var(--text-grey-text, #818181);
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: 25px;
    line-height: normal;
    opacity: 0.5;
  }

  button.label:hover {
    cursor: pointer;
  }

  .hotel-label {
    background: none;
    border: none;
  }

  @media only screen and (width <= 720px) {
    .search-section {
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
