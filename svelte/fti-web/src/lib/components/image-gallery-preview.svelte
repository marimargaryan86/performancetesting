<script lang="ts">
  /* eslint-disable @typescript-eslint/no-unused-vars */

  /* TODO: Refactor and tidy up this component to meet the design reuqirements */

  /**
   * A Svelte component that displays a featured hotel's image gallery. It showcases a primary selected image
   * along with thumbnails for other images. Users can open a more extensive image gallery by interacting with
   * these thumbnails.
   *
   * Features:
   * - Displays the first image from the `hotelInfo.images` array as the default selected image.
   * - Allows users to open a gallery view to a specific image by clicking on thumbnails of up to four additional images.
   * - Provides an overlay on the last visible thumbnail if more than five images exist, indicating the number of
   *   additional images available.
   * - Responsive design with flex and grid layouts to adapt to varying screen sizes.
   *
   */

  import type { FeaturedPackage } from "$lib/models/common";
  import { createEventDispatcher } from "svelte";

  interface FeaturedPackageWithReview extends FeaturedPackage {
    reviewScore: number;
    reviewText: string;
    reviewCount: number;
    images: string[];
  }

  export let hotelInfo: FeaturedPackageWithReview;
  export let selectedImage = hotelInfo.images[0];

  interface DispatchEvents {
    close: undefined;
    open: number;
  }
  const dispatch = createEventDispatcher<DispatchEvents>();

  function openImageGallery(index: number): void {
    dispatch("open", index);
  }

  function closeImageGallery() {
    dispatch("close");
  }
</script>

<div class="hotel-images-container">
  <div class="hotel-images-container-left">
    <button
      class="image-button"
      on:click={() => openImageGallery(0)}
      aria-label="Open Image Gallery"
    >
      <!-- svelte-ignore a11y-img-redundant-alt -->
      <img class="hotel-images-container-left" src={selectedImage} alt="Selected Hotel Image" />
    </button>
  </div>
  <div class="hotel-images-container-right">
    {#each hotelInfo.images as image, index (image)}
      {#if index !== 0 && index < 5}
        <button
          class="thumbnail"
          class:selected={selectedImage === image}
          on:click={() => {
            openImageGallery(index);
          }}
          aria-label={`Select Hotel Image ${index + 1}`}
        >
          <img class:thumbnail-opacity={index === 4} src={image} alt={`Hotel Image ${index + 1}`} />
          {#if index === 4}
            <div class="image-overlay"></div>
            <p class="gallery-overlay">View Gallery (+{hotelInfo.images.length - 5})</p>
          {/if}
        </button>
      {/if}
    {/each}
  </div>
</div>

<style>
  .hotel-images-container {
    display: flex;
    gap: 12px;
    max-height: 300;
  }

  .hotel-images-container .thumbnail {
    position: relative;
  }

  .hotel-images-container .thumbnail .gallery-overlay {
    position: relative;
    top: 50%;
    left: 50%;
    z-index: 1;
    color: white;
    font-weight: 600;
    font-size: 20px;
    font-family: "Plus Jakarta Sans";
    transform: translate(-50%, -50%);
  }

  .hotel-images-container .thumbnail .image-overlay {
    position: absolute;
    inset: 0;
    z-index: 1;
    margin-top: 7.5px;
    margin-right: 7.5px;
    margin-bottom: 7.5px;
    background-color: rgb(0 0 0 / 0.3);
  }

  .hotel-images-container-left {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 5px;
  }

  .hotel-images-container-right {
    display: grid;
    grid-template-rows: auto auto;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    align-content: start;
    width: 40%;
    height: 100%;
  }

  .image-button {
    border: none;
    background: transparent;
    padding: 0;
    margin: 0;
  }

  .thumbnail {
    position: relative;
    display: block;
    width: 100%;
    height: 100%;
    padding: 0;
    background: none;
    border: none;
    cursor: pointer;
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 5px;
  }

  .thumbnail.selected img {
    opacity: 1;
  }
</style>
