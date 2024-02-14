<script lang="ts">
  import FaSun from "svelte-icons/fa/FaSun.svelte";
  import FaCloudRain from "svelte-icons/fa/FaCloudRain.svelte";
  import FaRegHeart from "svelte-icons/fa/FaRegHeart.svelte";
  let activeFilter = "All";
  let categories = [
    "Any Weather",
    "Cold ❄️ -10-9ºC",
    "Cool ☁️ 10-15ºC ",
    "Warm ⛅ 16-24ºC",
    "Hot ☀️ 25-30ºC",
    "Very Hot 🔥 31ºC+",
  ];

  let results = [
    {
      name: "Cairo, Egypt",
      description: "7 nights, 5 star hotel, flights included",
      stars: 4,
      price: "£1,200",
      image: "/images/greece.jpeg",
      like: true,
    },
    {
      name: "Graz, Austria",
      description: "10 nights, all inclusive, flights included",
      stars: 5,
      price: "£1,500",
      image: "/images/beach.jpeg",
      like: false,
    },
    {
      name: "Cancun, Mexico",
      description: "3 nights, 4 star hotel, flights included",
      stars: 4,
      price: "£500",
      image: "/images/sand.jpeg",
      like: false,
    },
    {
      name: "Santorini, Greece",
      description: "7 nights, 5 star hotel, flights included",
      stars: 4,
      price: "£2,000",
      image: "/images/greece.jpeg",
      like: true,
    },
    {
      name: "Phuket, Thailand",
      description: "10 nights, 4 star hotel, flights included",
      stars: 3,
      price: "£1,000",
      image: "/images/beach.jpeg",
      like: true,
    },
  ];
</script>

<div class="packages-container">
  <h2>Travel weather forecast</h2>
  <div class="description-bar">
    <p class="description">
      Let our handy tool help you decide where to head for your next sunshine fix.
    </p>
    <div class="when-dropdown">
      <label for="when">When</label>
      <input type="date" id="when" />
    </div>
    <div class="where-dropdown">
      <label for="where">Where</label>
      <input type="text" id="where" placeholder="Anywhere" />
    </div>
  </div>
  <div class="packages-filter-container">
    <div class="packages-filter">
      {#each categories as category}
        <button class="category-button" class:active={category === activeFilter}>{category}</button>
      {/each}
    </div>
  </div>
  <div class="package-results">
    {#each results as result}
      <div class="package-card">
        <img class="package-image" src={result.image} alt={result.name} />
        <div class="temperature-box">
          <p>25°C</p>
        </div>
        <button class="heart-button">
          <FaRegHeart />
        </button>
        <div class="card-content">
          <div class="price-box">
            <p>from<span class="bold">&nbsp;{result.price}</span>pp</p>
          </div>
          <h3>{result.name}</h3>
          <div class="weather-box">
            <div class="sun">
              <div class="icon">
                <FaSun />
              </div>
              60%
            </div>
            <div class="rain">
              <div class="icon">
                <FaCloudRain />
              </div>
              20%
            </div>
            <button class="explore-button">Explore</button>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .packages-container {
    display: flex;
    flex-direction: column;
    width: calc(100% - 230px);
    margin: 80px auto 120px;
  }

  .packages-container h2 {
    margin-bottom: 5px;
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 700;
    font-size: 42px;
    font-style: normal;
    line-height: normal;
    text-transform: capitalize;
  }

  .description-bar {
    display: flex;
    gap: 20px;
    align-items: center;
    margin: 8px 0 22px;
  }

  .description {
    flex-grow: 1;
  }

  .when-dropdown {
    display: flex;
    flex-direction: column;
  }

  .where-dropdown {
    display: flex;
    flex-direction: column;
  }

  .packages-filter-container {
    padding-bottom: 40px;
  }

  .packages-filter {
    display: flex;
    gap: 16px;
  }

  .category-button {
    padding: 12px 22px;
    color: var(--text-dark-text);
    font-weight: 400;
    font-size: 14px;
    font-style: normal;
    line-height: normal;
    background: #f6f5f5;
    border: none;
    border-radius: 4px;
  }

  .category-button.active {
    background: rgb(234 113 33 / 0.08);
    border: 1px solid #ea7121;
  }

  .package-results {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .package-card {
    position: relative;
    border: 1px solid var(--dark-stroke, #c1b5b5);
    border-radius: 8px;
  }

  .temperature-box {
    position: absolute;
    top: 20px;
    left: 20px;
    color: white;
    background: rgb(0 0 0 / 0.4);
    border-radius: 8px;
  }

  .temperature-box p {
    margin: 0;
    padding: 12px 16px;
    font-weight: 500;
    font-size: 18px;
  }

  .heart-button {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 42px;
    color: #ea7121;
    background: none;
    border: none;
  }

  .heart-button:hover {
    cursor: pointer;
  }

  .package-image {
    width: 100%;
    height: 340px;
    object-fit: cover;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }

  .card-content {
    position: relative;
    padding: 20px 24px 42px;
  }

  .card-content h3 {
    margin: 6px 0 8px;
  }

  .weather-box {
    display: flex;
  }

  .sun,
  .rain {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-right: 20px;
  }

  .rain {
    flex-grow: 1;
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
  }

  .price-box {
    position: absolute;
    top: -27px;
    right: 20px;
    display: flex;
    align-items: center;
    height: 40px;
    padding: 2px 8px;
    color: white;
    background: #ea7121;
    border-radius: 4px;
  }

  .price-box p {
    margin: 0;
    font-weight: 300;
    font-size: 12px;
  }

  .bold {
    padding-left: 4px;
    font-weight: 600;
    font-size: 18px;
  }

  .explore-button {
    position: relative;
    top: 12px;
    padding: 12px 18px;
    color: var(--text-dark-text);
    font-weight: 500;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    border: 1px solid var(--text-dark-text);
    border-radius: 8px;
  }
</style>
