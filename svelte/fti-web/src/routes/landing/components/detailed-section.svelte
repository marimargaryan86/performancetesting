<script lang="ts">
  import FaRegCalendarAlt from "svelte-icons/fa/FaRegCalendarAlt.svelte";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";
  import StarRating from "components/star-rating.svelte";
  import ArrowsComponent from "components/arrows-component.svelte";
  let items = [
    {
      name: "Canareef Resort Maldives",
      location: " Maldives - Addu Atoll / Herathera",
      length: "7 nights",
      stars: 4,
      price: "£1,800",
      description:
        "This package includes a scheduled flight with a renowned airline from/to Germany and back. You will be staying 7 nights in a 4-star Canareef Maldives Resort in the Sunrise Beach Villa with all inclusive. We offer a 15-minute jet lag massage as well as a complimentary drink upon arrival.",
    },
  ];
</script>

<div class="detailed-section">
  {#each items as item}
    <div class="item-container">
      <div class="tv-label">
        <p>As seen on sonnenklar.tv</p>
      </div>
      <div class="item-label">
        <p class="item-title">
          {item.name}
        </p>
        <div class="item-buttons">
          <ArrowsComponent />
        </div>
      </div>
      <div class="item-location-header">
        <!-- Convert this to grid -->
        <div class="item-location">
          <div class="location-icon">
            <FaMapMarkerAlt />
          </div>
          {item.location}
        </div>
        <div class="trip-length">
          <div class="location-icon">
            <FaRegCalendarAlt />
          </div>
          {item.length} nights
        </div>
        <div class="stars">
          <StarRating starRating={item.stars} />
        </div>
      </div>
      <div class="item-images">
        <div class="image-grid">
          <div class="image-left">
            <img src="/images/detailed-example.png" alt="beach" />
          </div>
          <div class="image-right">
            <div class="image-top">
              <img src="/images/detailed-example.png" alt="beach" />
            </div>
            <div class="image-bottom">
              <img src="/images/detailed-example.png" alt="beach" />
            </div>
          </div>
        </div>
      </div>
      <div class="item-description">
        <div class="item-description-content">
          <div class="item-description-title">Whats Included?</div>
          <div class="item-description-desc">
            {item.description}
          </div>
        </div>
        <div class="item-price">
          <p>
            from <span class="bold">{item.price}</span>pp
          </p>
          <button class="explore-button"> Explore this package </button>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  .detailed-section {
    display: flex;
    background: #f2fbff;
    padding: 100px 175px;
    flex-direction: row;
    gap: 70px;
  }
  .item-container {
    width: 75%;
  }
  .tv-label p {
    color: #0078ff;
    font-size: 18px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
    text-transform: capitalize;
  }
  .item-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
    width: 100%;
  }
  .item-buttons {
    display: flex;
    gap: 8px;
  }
  .item-title {
    color: var(--Text-Dark-Text, #1c1c1c);
    font-family: "Plus Jakarta Sans";
    font-size: 40px;
    font-style: normal;
    font-weight: 700;
    line-height: normal;
    margin: 0;
  }

  .item-location-header {
    display: flex;
    gap: 20px;
    align-items: center;
    margin: 10px 0;
  }
  .item-location {
    display: flex;
    gap: 8px;
    color: var(--Text-Dark-Text, #1c1c1c);
    font-style: normal;
    font-weight: 600;
    line-height: normal;
  }
  .location-icon {
    width: 14px;
  }
  .trip-length {
    display: flex;
    gap: 8px;
    overflow: hidden;
    color: var(--Text-Dark-Text, #1c1c1c);
    text-overflow: ellipsis;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    font-weight: 600;
    line-height: normal;
  }

  .image-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .image-left img {
    width: 478px;
    height: 420px;
    object-fit: cover;
  }

  .image-right {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .image-right img {
    width: 375px;
    height: 198px;
    object-fit: cover;
  }

  .item-description {
    display: flex;
    gap: 120px;
    padding: 50px 0 0;
  }

  .item-description-title {
    color: var(--Text-Dark-Text, #1c1c1c);
    font-size: 36px;
    font-style: normal;
    font-weight: 700;
    line-height: 48px;
    text-transform: capitalize;
  }

  .item-description-content {
    flex-basis: 70%;
  }

  .item-description-desc {
    color: #1c1c1c;
    font-size: 18px;
    font-style: normal;
    font-weight: 400;
    line-height: 28px;
    letter-spacing: 0.3px;
    margin-top: 16px;
  }

  .item-price p {
    color: black;
  }

  .explore-button {
    border-radius: 8px;
    background: #ea7121;
    color: white;
    padding: 18px 18px;
    border: none;
    font-size: 16px;
    font-weight: 500;
  }

  .bold {
    font-weight: 700;
    padding: 0 2px;
  }
</style>
