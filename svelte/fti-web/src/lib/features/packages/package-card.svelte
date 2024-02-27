<script lang="ts">
  import StarRating from "$lib/components/star-rating.svelte";
  import type { Package } from "$lib/models/common";
  import FaRegHeart from "svelte-icons/fa/FaRegHeart.svelte";

  export let holiday: Package;
</script>

<div class="package-card">
  <img class="package-image" src={holiday.image} alt={holiday.name} />
  <button class="heart-button">
    <FaRegHeart />
  </button>
  <div class="card-content">
    <div class="price-box">
      <p>from<span class="bold">&nbsp;€{holiday.price}</span>pp</p>
    </div>
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
    width: 60px;
    color: #ea7121;
    background: none;
    border: none;
  }

  .heart-button:hover {
    cursor: pointer;
  }

  .package-image {
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
