<script lang="ts">
  import ArrowsComponent from "components/arrows-component.svelte";
  import StarRating from "components/star-rating.svelte";
  import FaRegHeart from "svelte-icons/fa/FaRegHeart.svelte";
  let activeFilter = "All";
  let categories = [
    "All",
    "Family Holidays",
    "Cruises",
    "Couples",
    "City Breaks",
    "All Inclusive",
    "Tours",
    "Adventures",
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

  let setContainerScroll = ({ detail }: { detail: boolean }): void => {
    const container = document.querySelector(".package-results");
    const delta = detail ? 352 : -352;
    if (container) {
      const currentScroll = container.scrollLeft;
      const newScroll = currentScroll + delta;
      container.scrollTo({ left: newScroll, behavior: "smooth" });
    }
  };
</script>

<div class="packages-container">
  <h2>Packages you'll love</h2>
  <div class="packages-filter-container">
    <div class="packages-filter">
      {#each categories as category}
        <button class="category-button" class:active={category === activeFilter}>{category}</button>
      {/each}
    </div>
    <ArrowsComponent on:scroll={setContainerScroll} />
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
  <div class="button-container">
    <button class="packages-button">See all packages</button>
  </div>
</div>

<style>
  .packages-container {
    display: flex;
    flex-direction: column;
    width: calc(100% - 230px);
    margin: 0 auto 120px;
  }

  .packages-container h2 {
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 700;
    font-size: 36px;
    font-style: normal;
    line-height: 44px; /* 122.222% */
  }

  .packages-filter-container {
    display: flex;
    padding-bottom: 40px;
  }

  .packages-filter {
    display: flex;
    flex-grow: 1;
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
    display: flex;
    gap: 20px;
    overflow-x: scroll;
  }

  .package-card {
    position: relative;
    width: calc(33vw - 90px);
    border: 1px solid var(--dark-stroke, #c1b5b5);
    border-radius: 8px;
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
    /* width: calc((100% / 3) - 332px); */
    width: calc(33vw - 90px);
    height: 340px;
    object-fit: cover;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }

  .card-content {
    position: relative;
    padding: 20px 24px;
  }

  .price-box {
    position: absolute;
    top: -36px;
    right: 20px;
    display: flex;
    align-items: center;
    height: 48px;
    padding: 8px 16px;
    color: white;
    background: #ea7121;
    border-radius: 4px;
  }

  .price-box p {
    margin: 0;
    font-weight: 300;
    font-size: 16px;
  }

  .bold {
    padding-left: 4px;
    font-weight: 600;
    font-size: 22px;
  }

  .button-container {
    display: flex;
    justify-content: center;
    margin: 32px 0;
  }

  .packages-button {
    width: 15%;
    padding: 8px 16px;
    background: none;
    border: 1px solid #1c1c1c;
    border-radius: 4px;
  }

  .packages-button:hover {
    cursor: pointer;
  }
</style>
