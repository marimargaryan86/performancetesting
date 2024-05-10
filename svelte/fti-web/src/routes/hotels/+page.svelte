<script context="module" lang="ts">
  export type HotelOffer = {
    title: string;
    description: string;
  };
  export interface FeaturedPackageWithReview extends FeaturedPackage {
    reviewScore: number;
    reviewText: string;
    reviewCount: number;
    images: string[];
    suites: number;
    lifts: number;
    floors: number;
    pointsOfInterest: string[];
    distanceToAirport: string;
    hotelOffer: HotelOffer;
  }

  export const MOCK_HOTEL_INFO: FeaturedPackageWithReview = {
    name: "White Goose Hotel",
    location: "Indonesia, Bali",
    length: "10 nights",
    stars: 4,
    price: "1200",
    description:
      "White Goose Boutique Hotel is all about the laid-back island lifestyle. We offer a fresh boutique accommodation experience located in the heart of Canggu, just a few leisurely steps, skips or hops away from Berawa's crashing surf and sandy beach.",
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
    ],
    suites: 18,
    lifts: 2,
    floors: 3,
    pointsOfInterest: ["Berawa Beach", "Batu Belig Beach", "Nelayan Beach"],
    distanceToAirport:
      "The nearest airport is Ngurah Rai International Airport, 15 km from the hotel.",
    hotelOffer: {
      title: "Exclusive honeymoon spa offer",
      description: "Free 30 min Spa treatment for 2 guests staying 1 week or longer",
    },
  };
</script>

<script lang="ts">
  /* eslint-disable @typescript-eslint/no-unused-vars */
  import type { FeaturedPackage } from "$lib/models/common";
  import ImageGalleryPreview from "$lib/components/image-gallery-preview.svelte";
  import SharePackageModal from "$lib/components/share-modal.svelte";
  import ImageGalleryModal from "$lib/components/image-gallery-modal.svelte";

  import { renderStars } from "$lib/helpers/common";

  import Icon from "$lib/components/icon.svelte";
  import { goto } from "$app/navigation";
  import { writable } from "svelte/store";

  type PackageTab = "Overview" | "Rooms" | "Reviews";

  const activePackageTab = writable<PackageTab>("Overview");
  // eslint-disable-next-line svelte/valid-prop-names-in-kit-pages
  export let hotelInfo: FeaturedPackageWithReview = MOCK_HOTEL_INFO;

  function setActivePackageTab(tab: PackageTab): void {
    activePackageTab.set(tab);
  }

  function navigateToPaymentScreen(): void {
    localStorage.clear();
    goto("/payment");
  }

  let selectedImage = hotelInfo.images[0];
  let selectedIndex = 0;

  let isPackageLiked = false;

  let currentBookingStep = 1;

  let showShareModal = false;
  let showImageGallery = false;
  let showFlightDetailsModal = false;

  const toggleLike = (): void => {
    isPackageLiked = !isPackageLiked;
  };

  const openShareModal = (): void => {
    showShareModal = true;
  };

  const closeShareModal = (): void => {
    showShareModal = false;
  };

  const openFlightDetailsModal = (): void => {
    showFlightDetailsModal = true;
  };

  const closeFlightDetailsModal = (): void => {
    showFlightDetailsModal = false;
  };

  const setBookingStep = (bookingStepId: number): void => {
    currentBookingStep = bookingStepId;
  };

  function openImageGallery(index: number): void {
    selectedIndex = index;
    showImageGallery = true;
  }

  function closeImageGallery() {
    showImageGallery = false;
  }
</script>

<SharePackageModal show={showShareModal} {hotelInfo} onClose={closeShareModal} />
<ImageGalleryModal
  images={hotelInfo.images}
  isOpen={showImageGallery}
  initialIndex={selectedIndex}
  on:close={closeImageGallery}
/>

<div class="page">
  <div class="hotel-header">
    <div class="hotel-info">
      <div class="back-link">
        <button on:click={() => goto("/search")}>
          <Icon variant="left-back-arrow" size="16px" color="#01A5C9" />
          Back to results
        </button>
      </div>
      <div class="hotel-title">
        <h1>{hotelInfo.name}</h1>
        <div class="stars">
          {#each renderStars(hotelInfo.stars) as star}
            <span>{star}</span>
          {/each}
        </div>
      </div>
      <div class="location-review">
        <span class="location">
          <Icon variant="location-icon" size="20px" color="#1C1B1F" />

          {hotelInfo.location}
        </span>
        <span class="review-score">{hotelInfo.reviewScore}</span>
        <span class="review-text">{hotelInfo.reviewText} ({hotelInfo.reviewCount})</span>
      </div>
    </div>
    <div class="button-container">
      <button
        class="action-button like-button"
        on:click={toggleLike}
        aria-label="Like"
        class:liked={isPackageLiked}
      >
        <Icon variant={"heart-full"} size="36px" color={isPackageLiked ? "#ff616f" : "#B3AAAA"} />
      </button>

      <button class="action-button share-button" on:click={openShareModal} aria-label="Share">
        <Icon variant="share-icon" size="30px" color="#000000" />
      </button>
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div on:click={navigateToPaymentScreen} class="proceed-button">Proceed to book</div>
    </div>
  </div>
  <ImageGalleryPreview
    {hotelInfo}
    {selectedImage}
    on:close={closeImageGallery}
    on:open={() => openImageGallery(selectedIndex)}
  />
  <div class="tabs-container">
    <nav>
      <button on:click={() => setActivePackageTab("Overview")}>Overview</button>
      <button on:click={() => setActivePackageTab("Rooms")}>Rooms</button>
      <button on:click={() => setActivePackageTab("Reviews")}>Reviews</button>
    </nav>
  </div>

  <div class="package-details">
    <div class="left-column"></div>
    <div class="right-column">
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div on:click={navigateToPaymentScreen} class="proceed-button-bottom">Proceed to book</div>
    </div>
  </div>
</div>

<style>
  .page {
    padding: 50px;
    background-color: white;
  }

  .package-details {
    display: flex;
  }

  .left-column {
    flex: 1;
    margin-right: 100px;
  }

  .right-column {
    flex: 1;
  }

  .back-link button {
    color: var(--colours-primary-blue, #01a5c9);
    font-weight: 500;
    font-size: 18px;
    font-family: "Plus Jakarta Sans";
    background: none;
    border: none;
  }

  .hotel-title {
    display: flex;
    align-items: center;
    color: #1a1b1c;
    font-weight: 700;
    font-size: 36px;
  }

  h1 {
    margin-right: 10px;
    padding: 0;
    font-weight: 600;
    font-size: 32px;
  }

  .location-review {
    color: #818181;
    font-weight: 500;
    font-size: 18px;
    font-family: "Plus Jakarta Sans";
  }

  .location {
    margin-right: 15px;
    padding-left: 5px;
  }

  .review-score {
    padding: 5px 6px;
    color: white;
    background-color: #8bc34a;
    border-radius: 8px;
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

  .hotel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
  }

  .button-container {
    display: flex;
    gap: 20px;
    align-items: center;
  }

  .action-button {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    cursor: pointer;
  }

  .like-button {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px;
    line-height: 0;
    background: none;
    border: none;
    cursor: pointer;
  }

  .proceed-button {
    display: inline-flex;
    flex-shrink: 0;
    gap: 6px;
    align-items: center;
    justify-content: center;
    height: 45px;
    padding: 10px 16px;
    color: #ffffff;
    font-weight: 500;
    font-size: 18px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: normal;
    background-color: #ea7121;
    border-radius: 5px;
  }

  .proceed-button:hover {
    background-color: var(--proceed-button-hover-bg-color, #e67e22);
  }

  nav button {
    margin: 0;
    padding: 0.5rem 1rem;
    color: var(--text-mid, #818181);
    font-weight: 500;
    font-size: 1rem;
    font-size: 22px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 32px;
    background: none;
    border: none;
    cursor: pointer;
  }

  nav button:focus {
    outline: none;
  }

  .tabs-container {
    margin-top: 15px;
    padding: 1rem 0;
  }

  .proceed-button-bottom {
    display: flex;
    gap: 40px;
    align-items: center;
    justify-content: center;
    width: 90%;
    margin-top: 45px;
    padding: 24px 32px;
    color: #ffffff;
    font-weight: 500;
    font-size: 22px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 32px;
    text-align: center;
    background: var(--colours-primary-orange, #ea7121);
    border-radius: 16px;
  }
</style>
