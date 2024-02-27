<script lang="ts">
  export let searchType: string = "combo";
</script>

<div class="search-header">
  <label class:selected={searchType === "combo"}>
    <input type="radio" value="combo" bind:group={searchType} hidden />
    <p>Holiday Packages</p>
  </label>
  <label class:selected={searchType === "hotels"}>
    <input type="radio" value="hotels" bind:group={searchType} hidden />
    <p>Hotels</p>
  </label>
  <label class:selected={searchType === "flights"}>
    <input type="radio" value="flights" bind:group={searchType} hidden />
    <p>Flights</p>
  </label>
</div>

<style>
  .search-header {
    display: flex;
    margin: 0 20px;
  }

  .search-header > label {
    display: flex;
    flex-basis: 27.5%;
    align-items: center;
    justify-content: center;
    background: var(--background-white);
  }

  .search-header > label:hover {
    cursor: pointer;
  }

  .search-header > label.selected {
    color: white;
    background: var(--text-primary-blue);
  }

  .search-header > label:first-of-type {
    flex-basis: 45%;
    border-top-left-radius: 8px;
  }

  .search-header > label:last-of-type {
    border-top-right-radius: 8px;
  }
</style>
