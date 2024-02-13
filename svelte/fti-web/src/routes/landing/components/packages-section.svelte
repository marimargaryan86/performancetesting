<script lang="ts">
  import ArrowsComponent from "components/arrows-component.svelte";
  import StarRating from "components/star-rating.svelte";
  import FaRegHeart from "svelte-icons/fa/FaRegHeart.svelte";
  let activeFilter = "All";
  let categories = [
    "All",
    "Family Holidays",
    "Cruises",
    "City Breaks",
    "All Inclusive",
    "Beach Holidays",
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
  <h2>Packages you'll love</h2>
  <div class="packages-filter-container">
    <div class="packages-filter">
      {#each categories as category}
        <button class="category-button" class:active={category === activeFilter}>{category}</button>
      {/each}
    </div>
    <ArrowsComponent />
  </div>
  <div class="package-results">
    {#each results as result}
      <div class="package-card">
        <img class="package-image" src={result.image} alt={result.name} />
        <button class="heart-button">
          <FaRegHeart />
        </button>
        <div class="card-content">
          <div class="price-box">
            <p>from<span class="bold">&nbsp;{result.price}</span>pp</p>
          </div>
          <div class="rating">
            <StarRating starRating={result.stars} />
          </div>
          <h3>{result.name}</h3>
          <p>{result.description}</p>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .packages-container {
    width: calc(100% - 230px);
    margin: 0 auto 120px;
    display: flex;
    flex-direction: column;
  }

  .packages-container h2 {
    color: var(--Text-Dark-Text, #1c1c1c);
    font-size: 36px;
    font-style: normal;
    font-weight: 700;
    line-height: 44px; /* 122.222% */
  }

  .packages-filter-container {
    display: flex;

    padding-bottom: 40px;
  }

  .packages-filter {
    flex-grow: 1;
    display: flex;
    gap: 16px;
  }

  .category-button {
    border-radius: 4px;
    background: #f6f5f5;
    color: var(--Text-Dark-Text);
    font-size: 14px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    border: none;
    padding: 12px 22px;
  }

  .category-button.active {
    border: 1px solid #ea7121;

    background: rgba(234, 113, 33, 0.08);
  }

  .package-results {
    display: flex;
    gap: 20px;
  }

  .package-card {
    border-radius: 8px;
    border: 1px solid var(--Dark-stroke, #c1b5b5);
    position: relative;
  }

  .heart-button {
    position: absolute;
    top: 20px;
    right: 20px;
    background: none;
    border: none;
    color: #ea7121;
    width: 42px;
  }

  .heart-button:hover {
    cursor: pointer;
  }

  .package-image {
    width: 332px;
    height: 340px;
    object-fit: cover;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }
  .card-content {
    padding: 20px 24px;
    position: relative;
  }
  .price-box {
    border-radius: 4px;
    background: #ea7121;
    color: white;
    padding: 8px 16px;
    position: absolute;
    top: -36px;
    right: 20px;
    height: 48px;
    display: flex;
    align-items: center;
  }
  .price-box p {
    font-weight: 300;
    font-size: 16px;
    margin: 0;
  }
  .bold {
    font-weight: 600;
    font-size: 22px;
    padding-left: 4px;
  }
</style>
