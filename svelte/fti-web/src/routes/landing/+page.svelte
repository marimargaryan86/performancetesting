<script lang="ts">
  import ExploreSection from "./components/explore-section.svelte";
  import WhyBook from "./components/why-book.svelte";
  import SearchBox from "./search-box.svelte";
  let searchType: string = "flights";
</script>

<div class="landing-header">
  <h1 class="title">Unlock Your Dream Getaway</h1>
  <p class="tagline">Discover the world - where your travel dreams meet unbeatable prices</p>

  <div class="search-container">
    <div class="search-header">
      <div class="search-header">
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
    </div>
    <SearchBox {searchType} />
  </div>
</div>
<div class="page">
  <ExploreSection />
  <WhyBook />
</div>

<style>
  .landing-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background-image: url("images/landing-background.jpeg");
    background-position: 0rem -20rem;
    background-size: cover;
    background-repeat: no-repeat;
  }
  .title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700;
    color: white;
    font-size: 64px;
    line-height: 64px;
  }
  .tagline {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 28px;
    color: white;
    line-height: 48px;
  }

  .search-container {
    width: 85%;
  }

  .search-header {
    display: flex;
    gap: 15px;
    margin-bottom: 16px;
  }
  .search-header > label {
    background-color: white;
    border-radius: 40px;
    color: var(--Text-Grey-Text, #818181);
    font-size: 16px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  .search-header > label:hover {
    background-color: var(--Text-Dark-Text, #1c1c1c);
    color: white;
    cursor: pointer;
  }
  .selected {
    background-color: var(--Text-Dark-Text, #1c1c1c);
    color: white;
  }

  .combo-search:checked + p {
    background-color: var(--Text-Dark-Text, #1c1c1c);
    color: white;
    margin: 0;
    border-radius: 40px;
  }

  .option-label {
    margin: 0;
    padding: 12px 25px;
  }

  .combo-search {
    background-color: white;
    color: white;
    border: none;
    padding: 8px 16px;
    font-size: 14px;
  }

  .page {
    margin-top: 120px;
    /* padding: 0 120px; */
  }
</style>
