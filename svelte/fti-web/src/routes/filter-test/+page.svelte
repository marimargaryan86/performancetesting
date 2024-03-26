<script lang="ts">
  import BoardFilter from "$lib/components/filters/board-filter.svelte";
  import FacilitiesFilter from "$lib/components/filters/facilities-filter.svelte";
  import PriceFilter from "$lib/components/filters/price-filter.svelte";
  import HotelRatingFilter from "$lib/components/filters/hotel-rating-filter.svelte";
  import ReviewScoreFilter from "$lib/components/filters/review-score-filter.svelte";
  import PerPerson from "$lib/components/filters/per-person.svelte";
</script>

<svelte:head>
  <title>Search Results</title>
</svelte:head>

<div class="page">
  <div class="filter-sidebar">
    <div class="filter-items">
      <PerPerson />
      <BoardFilter />
      <FacilitiesFilter />
      <HotelRatingFilter />
      <PriceFilter />
      <ReviewScoreFilter />
    </div>
  </div>
  <div class="main-content">
    <div class="search-results">
      <div class="test"></div>
      <div class="test"></div>
      <div class="test"></div>
    </div>
  </div>
</div>

<style>
  .page {
    display: flex;
    margin-top: 250px;
  }

  .filter-sidebar {
    width: 450px;
    background-color: #f5f5f5;
  }

  .main-content {
    flex-grow: 1;
  }

  .search-results {
    display: flex;
    flex-direction: column;
    gap: 20px;

    /* flex-wrap: wrap; */
  }

  .test {
    width: 700px;
    height: 150px;
    background: black;
  }
</style>
