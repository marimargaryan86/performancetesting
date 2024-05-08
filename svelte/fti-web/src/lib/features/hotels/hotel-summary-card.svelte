<script lang="ts">
  import Icon from "$lib/components/icon.svelte";
  import type { Accommodation } from "$lib/data/accommodations";
  import { renderStars } from "$lib/helpers/common";

  const acc: Accommodation | undefined = localStorage.getItem("accommodation")
    ? JSON.parse(localStorage.getItem("accommodation") as string)
    : undefined;

  export let hotelName: string = acc?.hotel.name || "White Goose Hotel";
  export let location: string = acc?.hotel.country
    ? `${acc?.hotel.country}, ${acc?.hotel.city}`
    : "Indonesia, Bali";
  export let checkInDate: string = "Tuesday 2nd April 2024";
  export let checkOutDate: string = "Friday 12th April 2024";
  export let nights: number = 10;
  export let boardType: string = "Half board";
  export let roomDetails: Array<{ adults: number; suiteType: string; view: string }> = [
    { adults: 2, suiteType: "Standard Suite", view: "Poolside View" },
    { adults: 2, suiteType: "Deluxe Suite", view: "Beach View" },
  ];
  export let stars: number = acc?.hotel.rating || 4;
  export let imageUrl: string = acc?.hotel
    ? `/images/accommodations/${acc?.hotel.id}.jpg`
    : "/images/hotel-gallery/1.jpg";
</script>

<div class="container">
  <h2>Summary</h2>

  <div class="accommodation-label">
    <Icon variant={"bed"} size={"24px"} color={"#1C1B1F"} />
    <p>Accommodation</p>
  </div>

  <div class="image-section">
    <img src={imageUrl} alt={`Image of ${hotelName}`} />
  </div>
  <div class="info-section">
    <div class="name-stars">
      <h3>{hotelName}</h3>
      <div class="stars">
        {#each renderStars(stars) as star}
          <span>{star}</span>
        {/each}
      </div>
    </div>
    <p class="location">
      <Icon variant={"location-icon"} size={"16px"} color={"#1C1C1C"} />
      {location}
    </p>

    <p class="dates">
      <b> Check in:</b>
      {checkInDate}
    </p>
    <p class="dates">
      <b>Check out:</b>
      {checkOutDate}
    </p>
    <p class="stay-details">
      <Icon variant={"half-moon"} color={"#1C1B1F"} size={"20px"} />
      {nights} nights
      <Icon variant={"restaurant"} color={"#1C1B1F"} size={"20px"} />

      {boardType}
    </p>
    <div class="room-info">
      {#each roomDetails as room, index}
        <h4>Room {index + 1}</h4>
        <p>{room.adults} Adults - {room.suiteType} - {room.view}</p>
      {/each}
    </div>
  </div>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    width: 90%;
    padding: 25px;
    overflow: hidden;
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgb(0 0 0 / 0.1);
  }

  h2 {
    color: var(--Meta-Neutral-900, #1a1b1c);
    font-weight: 700;
    font-size: 28px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 36px;
  }

  h3 {
    color: var(--text-dark, #1c1c1c);
    font-weight: 700;
    font-size: 24px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: normal;
    text-transform: capitalize;
  }

  h4 {
    color: var(--text-dark, #1c1c1c);
    font-weight: 600;
    font-size: 18px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: normal;
  }

  p {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 16px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 24px;
  }

  .accommodation-label {
    display: flex;
    gap: 15px;
    align-items: center;
    width: 77.5%;
    margin-bottom: 20px;
    padding-left: 15px;
    background: var(--colours-section-background, #f2fbff);
    border-radius: 8px;
  }

  .accommodation-label p {
    color: var(--text-dark, #1c1c1c);
    font-weight: 600;
    font-size: 16px;

    /* BigXtra/Label */
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: normal;
  }

  .image-section img {
    width: 80%;
    height: 175px;
    object-fit: cover;
    border-radius: 5px;
  }

  .info-section {
    padding: 1rem;
  }

  .name-stars {
    display: flex;
    gap: 7.5px;
    align-items: center;
  }

  .stars {
    gap: 15px;
    width: 45px;
    height: 45px;
    padding-top: 25px;
    fill: var(--colours-ratings-stars, #fbd148);
  }

  .location {
    gap: 5px;
    color: var(--text-mid, #818181);
    font-weight: 400;
    font-size: 16px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 24px;
  }

  .dates,
  .stay-details {
    padding-bottom: 5px;
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 16px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: 14px;
  }

  .room-info p {
    margin: 0.25rem 0;
    color: #333333;
    font-size: 0.9rem;
  }
</style>
