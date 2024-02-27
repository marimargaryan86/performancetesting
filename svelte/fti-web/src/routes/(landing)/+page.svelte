<script lang="ts">
  import ExploreSection from "$lib/features/explore/explore-section.svelte";
  import Packages from "$lib/features/packages/packages.svelte";
  import type { LandingPageModel } from "$lib/models/common";
  import Featured from "$lib/features/featured/featured.svelte";
  import KeyFeatures from "$lib/features/key-features/key-features.svelte";
  import WeatherForecast from "$lib/features/weather-forecast/weather-forecast.svelte";
  import SearchBox from "$lib/features/search-box/search-box.svelte";

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
  <Featured {featuredPackages} />
  <KeyFeatures />
  <WeatherForecast {weatherHolidays} />
</div>
