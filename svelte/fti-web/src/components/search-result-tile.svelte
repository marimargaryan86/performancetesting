<script lang="ts">
  import StarRating from "$lib/components/star-rating.svelte";
  import { amentitiesIconMap } from "$lib/data/constants";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";

  const item = {
    name: "The Kuta Beach Hotel - Managed by Accor",
    location: "Kuta, Bali",
    rating: 3,
    reviews: 35,
    checkIn: "7 Feb 2024",
    checkOut: "12 Feb 2024",
    amenities: [
      {
        label: "Near the beach",
        icon: "beach",
      },
      {
        label: "Spa",
        icon: "spa",
      },
      {
        label: "2 Communal Pools",
        icon: "pool",
      },
      {
        label: "24h Gym",
        icon: "gym",
      },
    ],
    cancellationFee: "Small cancellation fee",
    rebook: "Rebook Flexibility",
    included: ["flight", "hotel", "transfer", "luggage"],
    price: 79,
  };
</script>

<div class="search-result-tile">
  <div class="search-result-tile-gallery">
    <img src="https://via.placeholder.com/254" alt="Placeholder" />
  </div>
  <div class="search-result-tile-content">
    <div class="search-result-tile-content-details">
      <span class="hotel-name">{item.name}</span>
      <div class="hotel-location">
        <div class="location-icon">
          <FaMapMarkerAlt size={2} />
        </div>
        <span class="hotel-location-label">{item.location}</span>
      </div>
      <div class="hotel-rating">
        <!-- logo -->
        <img src="/icons/big-xtra-reviews.svg" alt="Big Xtra Reviews" />
        <StarRating starRating={3} />
        <span class="hotel-reviews">35 reviews</span>
      </div>
    </div>
    <div class="amenities-container">
      <div class="length-of-stay">
        <img src="/icons/amenities/half-moon.svg" alt="Half Moon" />
        <span>7 Feb 2024 (5 nights)</span>
      </div>
      <div class="amenity-list">
        {#each item.amenities as amenity}
          <div class="amenity-item">
            <img src={`/icons/amenities/${amenity.icon}.svg`} alt={amenity.label} />
            <span class="amenity-label">{amenity.label}</span>
          </div>
        {/each}
      </div>
    </div>
    <hr class="divider" />
    <div class="booking-details">
      <div class="information">
        <div class="booking-flexibility">
          <div class="cancellation-fee">
            <img src={amentitiesIconMap.tick} alt="Tick" />
            <span>{item.cancellationFee}</span>
          </div>
          <div class="rebook-flex">
            <img src={amentitiesIconMap.tick} alt="Tick" />
            <span>{item.rebook}</span>
          </div>
        </div>
        <div class="search-result-tile-content-package">
          <span>Whats Included:</span>
          <div class="included-items">
            {#each item.included as includedItem}
              <div class="included-item">
                <img src={`/icons/${includedItem}.svg`} alt={includedItem} />
              </div>
            {/each}
          </div>
        </div>
      </div>
      <div class="pricing">
        <span>Total from: <b class="price-label">€{item.price}</b>/ pp</span>
        <button>See Offer</button>
      </div>
    </div>
  </div>
</div>

<style>
  .search-result-tile {
    display: flex;
    gap: 32px;
    max-height: 254px;
    background: var(--colours-background-white, #ffffff);
    border-radius: 8px;
  }

  .search-result-tile-content {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 24px 24px 24px 0;
  }

  .search-result-tile-content-details {
    display: flex;
    flex-direction: column;
  }

  .hotel-name {
    color: var(--text-meta-neutral, #1a1b1c);
    font-weight: 600;
    font-size: 18px;
  }

  .hotel-location {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    color: var(--text-mid, #818181);
    font-weight: 400;
    font-size: 14px;
  }

  .location-icon {
    width: 12px;
    color: black;
  }

  .hotel-rating {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .hotel-rating :global(.stars-container) {
    margin: 8px 0;
  }

  .hotel-reviews {
    display: flex;
    color: var(--text-mid, #818181);
    font-weight: 500;
    font-size: 14px;
  }

  .length-of-stay {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .amenities-container {
    display: flex;
    gap: 8px;
  }

  .amenities-container img {
    width: 14px;
  }

  .length-of-stay span {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 14px;
    line-height: 20px; /* 166.667% */
  }

  .amenity-list {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .amenity-item {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .amenity-label {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 14px;
    line-height: 20px; /* 166.667% */
  }

  .divider {
    width: 100%;
    border: 0.05rem solid var(--divider-color, #e4e6e9);
  }

  .information {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .booking-flexibility {
    display: flex;
    gap: 22px;
  }

  .booking-flexibility div {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .search-result-tile-content-package {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .booking-details {
    display: flex;
    justify-content: space-between;
  }

  .included-items {
    display: flex;
    gap: 22px;
  }

  .included-item {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--colours-section-background, #f2fbff);
    border-radius: 28px;
  }

  :not(:last-child).included-item::after {
    position: absolute;
    left: 35px;
    content: "+";
  }

  .included-item img {
    color: var(--colours-primary-blue, #01a5c9);
  }

  .pricing {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .pricing button {
    margin: 2px 10px;
    padding: 8px 12px;
    color: white;
    font-size: 14px;
    background: var(--colours-primary-orange, #ea7121);
    border: none;
    border-radius: 4px;
  }

  .price-label {
    color: var(--colours-primary-orange, #ea7121);
    font-size: 24px;
  }
</style>
