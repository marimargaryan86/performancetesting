<script lang="ts">
  import { onMount } from "svelte";

  onMount(async (): Promise<void> => {
    const response = await fetch("/images");
    const imagePaths = await response.json();
    hotelInfo.images = imagePaths;
    selectedImage = hotelInfo.images[0];
  });

  interface HotelInfo {
    name: string;
    stars: number;
    location: string;
    reviewScore: number;
    reviewText: string;
    reviewCount: number;
    images: string[];
  }

  let hotelInfo: HotelInfo = {
    name: "White Goose Hotel",
    stars: 4,
    location: "Indonesia, Bali",
    reviewScore: 4.8,
    reviewText: "Very good",
    reviewCount: 35,
    images: [
      "/images/hotel-gallery/1.jpg",
      "/images/hotel-gallery/2.jpg",
      "/images/hotel-gallery/3.jpg",
      "/images/hotel-gallery/4.jpg",
      "/images/hotel-gallery/5.jpg",
      "/images/hotel-gallery/6.jpg",
      "/images/hotel-gallery/7.jpg",
      "/images/hotel-gallery/8.jpg",
      "/images/hotel-gallery/9.jpg",
      "/images/hotel-gallery/10.jpg",
      "/images/hotel-gallery/11.jpg",
    ],
  };

  let selectedImage = hotelInfo.images[0];

  let currentBookingStep = 1;

  const bookingSteps = [
    { id: 1, name: "Flight & Room" },
    { id: 2, name: "Select Extras" },
    { id: 3, name: "Passengers & Payment" },
    { id: 4, name: "Review & Confirmation" },
  ];

  const setBookingStep = (bookingStepId: number): void => {
    currentBookingStep = bookingStepId;
  };

  const renderStars = (stars: number): string[] => Array.from({ length: stars }, () => "⭐");
</script>

<div class="page">
  <div class="booking-steps-container">
    <nav class="booking-nav">
      <ul>
        {#each bookingSteps as step, index}
          <button
            class:active={currentBookingStep === step.id}
            on:click={() => setBookingStep(step.id)}
            class="step-button"
          >
            <div class="step">
              <div class="step-number">{step.id}</div>
              <div class="step-name">{step.name}</div>
            </div>
            {#if index < bookingSteps.length - 1}
              <div class="step-separator"></div>
            {/if}
          </button>
        {/each}
      </ul>
    </nav>
  </div>
  <div class="back-link">
    <button>← Back to results</button>
  </div>

  <div class="hotel-info">
    <div class="hotel-title">
      <h1>{hotelInfo.name}</h1>
      <div class="stars">
        {#each renderStars(hotelInfo.stars) as star}
          <span>{star}</span>
        {/each}
      </div>
    </div>
    <div class="location-review">
      <span class="location">📍 {hotelInfo.location}</span>
      <span class="review-score">{hotelInfo.reviewScore}</span>
      <span class="review-text">{hotelInfo.reviewText} ({hotelInfo.reviewCount})</span>
    </div>
  </div>
  <div class="image-gallery">
    <!-- svelte-ignore a11y-img-redundant-alt -->
    <img class="selected-image" src={selectedImage} alt="Selected Hotel Image" />

    <div class="thumbnails">
      {#each hotelInfo.images as image, index (image)}
        <button
          class="thumbnail"
          class:selected={selectedImage === image}
          on:click={() => (selectedImage = image)}
          aria-label={`Select Hotel Image ${index + 1}`}
        >
          <img src={image} alt={`Hotel Image ${index + 1}`} />
        </button>
      {/each}
    </div>
  </div>
</div>

<style>
  .page {
    padding: 50px;
    background-color: white;
  }

  .booking-steps-container {
    display: flex;
    justify-content: center;
    padding: 20px 0;
    border-bottom: 1px solid #d0d9df;
    margin-bottom: 30px;
  }

  .booking-nav ul {
    list-style: none;
    display: flex;
    padding: 0;
    margin: 0;
    position: relative;
  }

  .booking-nav button {
    display: flex;
    align-items: center;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
  }

  .step {
    display: flex;
    align-items: center;
    padding: 10px 20px;
  }

  .step-number {
    width: 25px;
    height: 25px;
    border-radius: 50%;
    background-color: #d8dadd;
    border: 2px solid #d8dadd;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    font-size: 12px;
  }

  .step-name {
    color: #7b8b9a;
    font-weight: 500;
    font-size: 16px;
  }

  .active .step-number {
    color: white;
    background-color: #01a5c9;
    border-color: #01a5c9;
  }

  .active .step-name {
    color: var(--text-dark, #1c1c1c);
  }

  .step-separator {
    height: 2px;
    background-color: #d0d9df;
    flex-grow: 1;
    margin: 0 8px;
  }

  .back-link button {
    color: var(--colours-primary-blue, #01a5c9);
    background: none;
    border: none;
    font-size: 18px;
  }

  .hotel-info {
    font-family: Arial, sans-serif;
  }

  .hotel-title {
    display: flex;
    align-items: center;
    color: #1a1b1c;
    font-size: 36px;
    font-weight: 700;
  }

  h1 {
    font-size: 32px;
    margin-right: 10px;
    padding: 0;
    font-weight: 600;
  }

  .location-review {
    color: #818181;
    font-size: 18px;
    font-weight: 500;
  }

  .location {
    margin-right: 15px;
    padding-left: 5px;
  }

  .review-score {
    background-color: #8bc34a;
    color: white;
    border-radius: 8px;
    padding: 5px 6px;
  }

  .review-text {
    margin-left: 12.5px;
    color: #757575;
    font-size: 15px;
  }

  .stars {
    color: yellow;
    font-size: 20px;
  }

  .image-gallery {
    margin-top: 20px;
  }

  .selected-image {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    border-radius: 5px;
    margin-bottom: 10px;
  }

  .thumbnails {
    display: flex;
    overflow-x: auto;
  }

  .thumbnail {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .thumbnail img {
    width: 100px;
    height: 100px;
    object-fit: cover;
    margin-right: 5px;
    border-radius: 5px;
    opacity: 0.6;
    transition: opacity 0.3s ease;
  }

  .thumbnail.selected img {
    opacity: 1;
  }
</style>
