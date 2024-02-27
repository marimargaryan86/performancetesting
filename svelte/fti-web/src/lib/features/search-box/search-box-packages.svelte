<script lang="ts">
  import OriginSelect from "./components/origin-select.svelte";
  import DateSelect from "./components/date-select.svelte";
  import HotelSelect from "./components/hotel-select.svelte";
  import DestinationSelect from "./components/destination-select.svelte";
</script>

<div class="search-container">
  <OriginSelect />
  <DestinationSelect />
  <DateSelect />
  <HotelSelect />
</div>

<style>
  .search-container {
    position: relative;
    display: flex;
    flex: 1;
    gap: 20px;
  }

  @media only screen and (width <= 720px) {
    .search-container {
      flex-direction: column;
      gap: 20px;
    }

    :global(.dropdown) {
      z-index: 99;
    }
  }
</style>
