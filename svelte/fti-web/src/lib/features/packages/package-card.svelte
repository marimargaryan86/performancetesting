<script context="module" lang="ts">
  /**
   * Also removes any commas from the stringified price number.
   *
   */
  function getPriceSearchURL(holiday: Package): string {
    const sanitizedPrice = holiday.price.replace(/,/g, "");
    const params = new URLSearchParams({ maxPrice: sanitizedPrice });

    return `/search?${params.toString()}`;
  }
</script>

<script lang="ts">
  import Icon from "$lib/components/icon.svelte";
  import StarRating from "$lib/components/star-rating.svelte";
  import type { Package } from "$lib/models/common";

  export let holiday: Package;
  const priceSearchLink: string = getPriceSearchURL(holiday);
</script>

<div class="package-card">
  <img class="package-image" src={holiday.image} alt={holiday.name} />
  <button class="heart-button">
    <Icon variant="heart-full" />
  </button>
  <div class="card-content">
    <a href={priceSearchLink}>
      <button class="price-box">
        <p>from<span class="bold">&nbsp;€{holiday.price}</span>pp</p>
      </button>
    </a>
    <div class="rating">
      <StarRating starRating={holiday.stars} />
    </div>
    <h3>{holiday.name}</h3>
    <p>{holiday.description}</p>
  </div>
</div>

<style>
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
    width: 40px;
    color: #ea7121;
    background: none;
    border: none;
  }

  .heart-button:hover {
    cursor: pointer;
  }

  .package-image {
    width: 324px;
    height: 310px;
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
    top: -28px;
    right: 20px;
    display: flex;
    align-items: center;
    height: 48px;
    padding: 0 12px;
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

  @media only screen and (width <= 720px) {
    .package-card {
      width: 280px;
      min-width: 280px;
    }

    .package-image {
      width: 100%;
      height: 220px;
    }
  }
</style>
