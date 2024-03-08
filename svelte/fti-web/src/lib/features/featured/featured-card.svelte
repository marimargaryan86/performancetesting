<script lang="ts">
  import ArrowsComponent from "$lib/components/arrows-component.svelte";
  import StarRating from "$lib/components/star-rating.svelte";
  import type { FeaturedPackage, Scroll } from "$lib/models/common";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";

  export let featuredPackage: FeaturedPackage;
  export let scroll: Scroll;
</script>

<div class="featured-package">
  <div class="featured-package-header">
    <div class="packages-title-section">
      <div class="tv-label">As Seen On Sonneklar.tv</div>
      <div class="package-title">{featuredPackage.name}</div>
      <div class="package-details">
        <span class="package-destination">
          <div class="icon"><FaMapMarkerAlt /></div>
          {featuredPackage.location}
        </span>
        <span class="package-length">
          {featuredPackage.length}
        </span>
        <StarRating starRating={featuredPackage.stars} />
      </div>
    </div>
    <div class="arrows-component">
      <ArrowsComponent on:scroll={scroll.changePosition} />
    </div>
  </div>
  <div class="featured-package-card">
    <div class="package-gallery">
      <div class="image-left">
        <img src="/images/detailed-example.png" alt="beach" />
      </div>
      <div class="images-right">
        <div class="image-top">
          <img src="/images/detailed-example.png" alt="beach" />
        </div>
        <div class="image-bottom">
          <img src="/images/detailed-example.png" alt="beach" />
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .featured-package-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
  }

  .tv-label {
    padding: 12px 0;
    color: #0078ff;
    font-weight: 700;
    font-size: 16px;
  }

  .package-gallery {
    display: flex;
    flex-direction: row;
    gap: 16px;
  }

  .package-details {
    display: flex;
  }

  .package-details span {
    display: flex;
    gap: 8px;
    color: var(--text-dark-text);
    font-weight: 700;
  }

  .package-title {
    font-weight: 600;
    font-size: 28px;
  }

  .image-left img {
    width: 678px;
    height: 550px;
  }

  .images-right {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .images-right img {
    width: 333px;
    height: 267px;
  }

  .icon {
    width: 16px;
    margin: 0;
  }

  @media only screen and (width <= 720px) {
    .featured-package-header {
      flex-direction: column-reverse;
      align-items: flex-start;
    }

    .package-details {
      flex-direction: column;
      gap: 12px;
    }

    .package-gallery {
      flex-direction: column;
    }

    .package-gallery img {
      width: 325px;
      height: 200px;
    }

    .images-right {
      flex-direction: row;
    }

    .package-title {
      margin-bottom: 16px;
    }

    .images-right img {
      width: 160px;
      height: 140px;
    }

    :global(.package-details .stars-container) {
      margin: 0;
    }

    :global(.arrows-component) {
      display: flex;
      justify-content: flex-end;
      width: 100%;
    }
  }
</style>
