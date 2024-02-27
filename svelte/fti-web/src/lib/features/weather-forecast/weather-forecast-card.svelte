<script lang="ts">
  import type { WeatherHoliday } from "$lib/models/common";
  export let holiday: WeatherHoliday;
</script>

<div class="weather-forecast-card">
  <img src={holiday.image} alt={holiday.name} />
  <div class="card-details">
    <span class="card-location">
      {holiday.name}
    </span>
    <div class="weather-details">
      <div class="weather">
        <div class="sun">
          <img src="/icons/sun-icon.svg" alt="Sun" />
          80%
        </div>
        <div class="rain">
          <img src="/icons/raincloud-icon.svg" alt="Rain" />
          60%
        </div>
      </div>
      <div class="explore">
        <button class="explore-button">Explore</button>
      </div>
    </div>
  </div>
</div>

<style>
  .weather-forecast-card {
    display: flex;
    flex-direction: column;
    gap: 22px;
    width: 100%;
    background: #ffffff;
    border: 1px solid #c1b5b5;
    border-radius: 8px;
  }

  .weather-forecast-card > img {
    width: 448px;
    height: 469px;
  }

  .card-details {
    display: flex;
    flex-direction: column;
    width: 100%;
    padding: 16px;
  }

  .card-location {
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 16px;
  }

  .weather-details {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .explore-button {
    padding: 12px 20px;
    color: white;
    font-weight: 600;
    background: #ea7121;
    border-radius: 4px;
  }

  @media only screen and (width <= 720px) {
    .weather-forecast-card {
      flex-direction: row;
      gap: 2px;
    }

    .weather-forecast-card > img {
      width: 130px;
      min-width: 130px;
      height: 130px;
    }

    .weather-details {
      flex-direction: row;
      gap: 16px;
      margin-top: 30px;
    }

    .weather div {
      display: flex;
      gap: 8px;
      font-weight: 600;
    }
  }
</style>
