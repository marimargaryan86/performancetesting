<script lang="ts">
  import ExploreSection from "$lib/features/explore/explore-section.svelte";
  import Packages from "$lib/features/packages/packages.svelte";
  import type { LandingPageModel } from "$lib/models/common";
  import Featured from "$lib/features/featured/featured.svelte";
  import KeyFeatures from "$lib/features/key-features/key-features.svelte";
  import WeatherForecast from "$lib/features/weather-forecast/weather-forecast.svelte";
  import SearchBox from "$lib/features/search-box/search-box.svelte";
  import BudgetSelector from "$lib/features/budget-finder/budget-selector.svelte";

  export let data: LandingPageModel;

  const {
    holidayPackages: packages,
    holidayCategories: categories,
    featuredPackages,
    weatherHolidays,
  } = data.data;
</script>

<div class="page">
  <SearchBox />
  <ExploreSection />
  <Packages {categories} {packages} />
  <BudgetSelector />
  <Featured {featuredPackages} />
  <KeyFeatures />
  <WeatherForecast {weatherHolidays} />
</div>

<style>
  .page {
    background-color: white;
  }

  @media only screen and (width <= 720px) {
    .page {
      padding: 0;
    }
  }
</style>
