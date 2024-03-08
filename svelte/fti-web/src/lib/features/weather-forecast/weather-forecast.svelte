<script lang="ts">
  import type { WeatherHoliday } from "$lib/models/common";
  import WeatherForecastHeader from "./weather-forecast-header.svelte";
  import WeatherForecastCard from "./weather-forecast-card.svelte";
  export let weatherHolidays: WeatherHoliday[];
</script>

<div class="weather-forecast">
  <WeatherForecastHeader />
  <div class="weather-forecast-container">
    {#each weatherHolidays as holiday}
      <WeatherForecastCard {holiday} />
    {/each}
  </div>
</div>

<style>
  .weather-forecast {
    padding: 0 76px 100px;
  }

  .weather-forecast-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 24px;
  }

  @media only screen and (width <= 720px) {
    .weather-forecast {
      padding: 0 20px;
    }

    .weather-forecast-container {
      grid-template-columns: repeat(1, 1fr);
      gap: 16px;
    }
  }
</style>
