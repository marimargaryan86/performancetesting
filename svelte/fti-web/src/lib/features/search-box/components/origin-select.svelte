<script lang="ts">
  import { getSearchOptionsCtx } from "$lib/stores/search-box.store";
  import { setDropdown } from "$lib/helpers/common";
  import OriginAirportSelect from "$lib/features/search-component/origin-airport-select.svelte";
  import { clickOutside } from "$lib/helpers/click-outside";
  import Icon from "$lib/components/icon.svelte";

  let dropdown: string = "";
  const clickOutsideHandler = (): string => handleSetDropdown("");
  const handleSetDropdown = (value: string): string => (dropdown = setDropdown(value));
  const searchOptions = getSearchOptionsCtx();
</script>

<div class="search-section location-section" use:clickOutside={clickOutsideHandler}>
  <div class="label">
    <div class="label-container">
      <div class="icon">
        <Icon variant="take-off" size="18px" color="black" />
      </div>
      <p class="label">Origin</p>
    </div>
    <input
      class="location-input"
      bind:value={$searchOptions.origin}
      placeholder="Flying from"
      on:focusin={handleSetDropdown.bind(handleSetDropdown, "location")}
    />
  </div>
  {#if dropdown === "location"}
    <OriginAirportSelect bind:selectedOrigin={$searchOptions.origin} bind:dropdown />
  {/if}
</div>

<style>
  .location-input {
    width: 90%;
    padding: 8px 0;
    color: #1c1c1c;
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    background-color: #ffffff;
    border: none;
  }

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
    color: var(--text-dark-text);
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
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
