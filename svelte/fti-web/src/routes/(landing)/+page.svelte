<script lang="ts">
  import DetailedSection from "./components/detailed-section.svelte";
  import ExploreSection from "./components/explore-section.svelte";
  import PackagesSection from "./components/packages-section.svelte";
  import TravelWeatherSection from "./components/travel-weather-section.svelte";
  import WhyBook from "./components/why-book.svelte";
  import SearchBox from "./components/search-box.svelte";
  let searchType: string = "flights";
</script>

<div class="landing-header">
  <div class="search-container">
    <div class="search-header">
      <!-- This won't work with +layout being in /routes. Hmm Don't have time to fix now will just change radios to buttons -->

      <label>
        <input
          type="radio"
          class:selected={searchType === "combo"}
          class="combo-search"
          value="combo"
          bind:group={searchType}
          hidden
        />

        <p class="option-label">Holiday Packages</p>
      </label>
      <label>
        <input
          type="radio"
          class:selected={searchType === "hotels"}
          class="combo-search"
          value="hotels"
          bind:group={searchType}
          hidden
        />
        <p class="option-label">Hotels</p>
      </label>
      <label>
        <input type="radio" class="combo-search" value="flights" bind:group={searchType} hidden />
        <p class="option-label">Flights</p>
      </label>
    </div>
    <SearchBox {searchType} />
  </div>
</div>
<div class="page">
  <ExploreSection />
  <PackagesSection />
  <DetailedSection />
  <WhyBook />
  <TravelWeatherSection />
</div>

<style>
  .landing-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 150px 0 60px;
    background-image: url("/images/landing-background.jpeg");
    background-repeat: no-repeat;
    background-position: 0 -20rem;
    background-size: cover;
  }

  .search-container {
    width: 85%;
  }

  .search-header {
    display: flex;

    /* gap: 15px; */
  }

  .search-header > label {
    color: var(--text-grey-text, #818181);
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    background-color: white;
  }

  .search-header > label:first-of-type {
    border-radius: 8px 0 0;
  }

  .search-header > label:last-of-type {
    border-radius: 0 8px 0 0;
  }

  .search-header > label:hover {
    color: white;
    background-color: #00a8cd;
    cursor: pointer;
  }

  .selected {
    color: white;
    background-color: var(--text-dark-text, #1c1c1c);
  }

  .combo-search:checked + p {
    margin: 0;
    color: white;
    background-color: #00a8cd;
  }

  .option-label {
    margin: 0;
    padding: 12px 25px;
  }

  .combo-search {
    padding: 8px 16px;
    color: white;
    font-size: 14px;
    background-color: white;
    border: none;
  }

  .page {
    margin-top: 120px;

    /* padding: 0 120px; */
  }
</style>
