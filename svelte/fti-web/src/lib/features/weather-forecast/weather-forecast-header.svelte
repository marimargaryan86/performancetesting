<script lang="ts">
  import { weatherCategories } from "$lib/data/constants";
  import { getMonthNames } from "$lib/helpers/common";
  // export let weatherHolidays: WeatherHoliday[];
  export let activeCategory: string = "Any Weather";

  const months = getMonthNames("en-US");

  function setActiveCategory(event: MouseEvent): void {
    const category = (event.target as HTMLButtonElement).id;
    activeCategory = category;
  }
</script>

<div class="forecast-header">
  <h3>Travel Weather Forecast</h3>
  <div class="forecast-options">
    <p class="description">
      Let our handy tool help you decide where to head for your next sunshine fix.
    </p>
    <div class="options">
      <div class="where-dropdown">
        <label for="where">Where?</label>
        <select id="where">
          <option value="anywhere">Anywhere</option>
          <option value="london">London</option>
        </select>
      </div>
      <div class="when-dropdown">
        <label for="when">When?</label>
        <select>
          <option value="anytime">Anytime</option>
          {#each months as month}
            <option value={month}>{month}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
  <div class="temperature-categories">
    {#each weatherCategories as category}
      <button
        class:active={activeCategory === category}
        class="category-button"
        id={category}
        on:click={setActiveCategory}>{category}</button
      >
    {/each}
  </div>
</div>

<style>
  .forecast-header {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding-top: 56px;
    color: var(--text-dark-text);
  }

  h3 {
    margin: 0;
    font-weight: 700;
    font-size: 32px;
    font-style: normal;
    line-height: normal;
  }

  p {
    margin: 0;
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: 24px; /* 150% */
  }

  .forecast-options {
    display: flex;
    gap: 20px;
  }

  .options {
    display: flex;
    width: 100%;
  }

  .options select {
    width: 100%;
    margin-top: 4px;
    padding: 14px 24px;
    color: var(--text-dark-text);
    font-size: 14px;
    line-height: 16px;
    background: #f6f5f5;
    border: 1px solid #a7a7a7;
    border-radius: 4px;
    appearance: initial;
  }

  label {
    color: var(--text-dark-text);
    font-weight: 500;
    font-size: 14px;
    font-style: normal;
    line-height: normal;
    opacity: 0.5;
  }

  .temperature-categories {
    display: flex;
    gap: 16px;
    overflow-x: scroll;
  }

  .temperature-categories::-webkit-scrollbar {
    display: none;
  }

  .category-button {
    min-width: fit-content;
    padding: 12px 24px;
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 13px;
    background: #f6f5f5;
    border: none;
    border-radius: 4px;
  }

  .category-button.active {
    background: rgb(234 113 33 / 0.08);
    border: 1px solid #ea7121;
  }

  @media only screen and (width <= 720px) {
    .forecast-options {
      flex-direction: column;
      align-items: center;
    }

    .options {
      flex-direction: column;
      gap: 16px;
    }
  }
</style>
