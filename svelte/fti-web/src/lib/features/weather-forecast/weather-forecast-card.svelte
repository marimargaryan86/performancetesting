<script context="module" lang="ts">
  function getDestinationSearchURL(holiday: WeatherHoliday): string {
    const encodedDestination = encodeURIComponent(holiday.name);
    const params = new URLSearchParams({ destination: encodedDestination });

    return `/search?${params.toString()}`;
  }
</script>

<script lang="ts">
  import type { WeatherHoliday } from "$lib/models/common";
  import Icon from "$lib/components/icon.svelte";

  export let holiday: WeatherHoliday;

  const destinationSearchLink: string = getDestinationSearchURL(holiday);
</script>

<div class="weather-forecast-card">
  <img src={holiday.image} alt={holiday.name} />
  <div class="overlay-content">
    <div class="top-section">
      <div class="temperature-tag">
        <span class="temperature">{holiday.temperature}</span>
        <span class="degree">°C</span>
      </div>
      <button class="heart-button">
        <Icon variant="heart-full" color="#e12c2c" />
      </button>
    </div>
    <div class="bottom-section">
      <div class="price-box">
        <p>from <span class="bold">€ 200</span>pp</p>
      </div>
    </div>
  </div>
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
        <a href={destinationSearchLink}>
          <button class="explore-button">Explore</button>
        </a>
      </div>
    </div>
  </div>
</div>

<style>
  .weather-forecast-card {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    background: #ffffff;
    border: 1px solid #c1b5b5;
    border-radius: 8px;
  }

  .weather-forecast-card > img {
    width: 100%;
    height: 300px;
    object-fit: cover;
  }

  .card-details {
    display: flex;
    flex-direction: column;
    padding: 16px;
  }

  .card-location {
    margin-bottom: 30px;
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 16px;
  }

  .weather-details {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
  }

  .weather {
    display: flex;
    gap: 18px;
    align-items: center;
  }

  .weather div {
    display: flex;
    gap: 6px;
  }

  .explore-button {
    padding: 12px 20px;
    color: var(--text-dark-text);
    font-weight: 600;
    background: none;
    border: 1px solid #000000;
    border-radius: 4px;
  }

  .overlay-content {
    position: absolute;
    width: 100%;
  }

  .top-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 12px 16px;
  }

  .temperature-tag {
    padding: 10px 12px;
    color: white;
    font-weight: 500;
    background: var(--colours-temperature-tags);
    border-radius: 8px;
  }

  .heart-button {
    width: 33px;
    height: 28px;
    color: #e12c2c;
    background: none;
    border: none;
  }

  .heart-button:hover {
    cursor: pointer;
  }

  :global(.heart-button > svg) {
    fill: red;
  }

  .bottom-section {
    position: absolute;
    top: 17rem;
    right: 2rem;
    padding: 0 10px;
    color: white;
    background: var(--colours-primary-orange);
    border-radius: 8px;
  }

  .price-box p {
    font-size: 0.8rem;
  }

  .price-box span {
    margin: 0 2px;
    font-weight: 600;
    font-size: 1.2rem;
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

    .card-details {
      width: 100%;
    }

    .weather-details {
      flex-direction: row;
      gap: 16px;
    }

    .weather {
      flex-direction: column;
    }

    .weather div {
      display: flex;
      gap: 8px;
      font-weight: 600;
    }

    .overlay-content {
      display: none;
    }
  }
</style>
