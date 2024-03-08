<script lang="ts">
  import OriginSelect from "./components/origin-select.svelte";
  import DestinationSelect from "./components/destination-select.svelte";
  import DateSelect from "./components/date-select.svelte";
  import PeopleSelect from "./components/people-select.svelte";

  let journeyType = "return";
</script>

<div class="flights-container">
  <div class="return-journey">
    <input type="radio" id="one-way" bind:group={journeyType} value="one-way" />
    <label for="one-way">One-way</label>
    <input type="radio" id="return" bind:group={journeyType} value="return" />
    <label for="return">Return</label>
  </div>
  <div class="search-container">
    <OriginSelect />
    {#if journeyType === "return"}
      <DestinationSelect />
    {/if}
    <DateSelect returnTrip={journeyType === "return"} />
    <PeopleSelect />
  </div>
</div>

<style>
  .flights-container {
    position: relative;
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  .search-container {
    position: relative;
    display: flex;
    flex: 1;
    gap: 20px;
  }

  .return-journey {
    margin-bottom: 24px;
  }

  @media only screen and (width <= 720px) {
    .search-container {
      flex-direction: column;
      gap: 20px;
      width: 100%;
    }

    :global(.dropdown) {
      z-index: 99;
    }
  }
</style>
