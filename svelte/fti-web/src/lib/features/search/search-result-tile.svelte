<script lang="ts">
  import type { Accommodation, AccommodationDetail } from "$lib/data/accommodations";
  import Icon from "$lib/components/icon.svelte";
  import type { AmenityIcons, IconTypes } from "$lib/models/common";

  export let accommodation: Accommodation;

  // TODO: figure out likes
  let likes: string[] = [];
  function setLike(id: string): void {
    if (!id) {
      return;
    }

    const existingIndex = likes.findIndex((like) => like === id);

    if (likes.includes(id)) {
      likes.splice(existingIndex, 1);
    } else {
      likes.push(id);
    }

    likes = [...likes];
  }

  // TODO: figure out rating strategy
  function getFilledStars(rating: number): number {
    return Math.floor(rating);
  }

  // TODO: ask design for specific icons, including checkmark and airport shuttle
  // eslint-disable-next-line complexity
  function getFacilityIconVariant(facility: string): IconTypes | AmenityIcons {
    switch (facility) {
      case "Swimming Pool":
      case "Rooftop Pool":
      case "Outdoor Pool":
        return "pool";
      case "Spa":
        return "spa";
      case "Beach Access":
        return "beach";
      case "Fitness Center":
        return "gym";
      case "Restaurant":
        return "restaurant";
      case "Bar":
        return "bar";
      case "Gym":
        return "gym";
      case "Garden":
        return "half-moon";
      case "Terrace":
        return "half-moon";
      case "Lake Access":
        return "beach";
      default:
        return "half-moon";
    }
  }

  function generatePrice(nextAccommodation: Accommodation): number {
    return nextAccommodation.accommodationDetails.reduce(
      (total: number, detail: AccommodationDetail) => total + detail.pricePerDay,
      0,
    );
  }
</script>

<div class="search-card">
  <div
    class="search-card-image"
    style={`background-image: url(/images/accommodations/${accommodation.hotel.id}.jpg)`}
  ></div>
  <div class="search-card-content">
    <h3>
      {accommodation?.hotel?.name}
      <button
        class="like"
        class:active={likes.includes(accommodation.hotel.id)}
        on:click|preventDefault={setLike.bind(setLike, accommodation?.hotel?.id)}
      >
        <Icon color="#1c1c1c" size="25px" variant="heart-full" />
      </button>
    </h3>
    <p class="description">
      <Icon color="#1c1c1c" size="14px" variant="location-icon" />
      {accommodation?.hotel?.address}
    </p>
    <p class="rating">
      <span>
        {#each Array([0, 1, 2, 3, 4]) as el, i}
          {#if el[i] < getFilledStars(accommodation.hotel.rating)}
            <Icon color="#1c1c1c" size="22px" variant="star" />
          {/if}
        {/each}
      </span>
      <span class="rating-value">{accommodation?.hotel?.rating}</span>
      {accommodation?.hotel?.category}
    </p>
    <ul class="facilities">
      {#each accommodation?.hotel?.facilities as facility}
        <li>
          <Icon color="#1c1c1c" size="12px" variant={getFacilityIconVariant(facility)} />
          {facility}
        </li>
      {/each}
    </ul>
    <ul class="board-types">
      {#each accommodation?.hotel?.boardType as boardType}
        <li>
          <!-- TODO: Should be checkmark -->
          <Icon color="#1c1c1c" size="16px" variant="half-moon" />
          {boardType}
        </li>
      {/each}
    </ul>
  </div>
  <div class="search-card-action">
    <div class="features">
      <Icon color="#1c1c1c" size="16px" variant="flight" />
      <Icon color="#1c1c1c" size="16px" variant="bed" />
      <!-- TODO: Should be bus. -->
      <Icon color="#1c1c1c" size="16px" variant="half-moon" />
    </div>
    <p>from <span>€{generatePrice(accommodation)}</span> /pp</p>
    <a href={`${accommodation?.hotel?.hotelUrl || ""}`}>Select</a>
  </div>
</div>

<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: "Plus Jakarta Sans", sans-serif;
  }

  .search-card {
    display: flex;
    align-items: stretch;
    width: 100%;
    overflow: hidden;
  }

  .search-card:last-child {
    margin-bottom: 0;
  }

  .search-card-image {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-width: 280px;
    max-width: 280px;
    background-repeat: no-repeat;
    background-size: 100% 100%;
  }

  .search-card-content {
    width: 100%;
    padding: 24px 24px 29px;
    border-right: 1px solid #e3e3e3;
  }

  .search-card-content h3 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    color: #1a1b1c;
    font-weight: 600;
    font-size: 18px;
    font-style: normal;
    line-height: normal;
  }

  .search-card-content h3 .like {
    margin-left: 16px;
    background: unset;
    border: 0;
    outline: unset;
  }

  .search-card-content h3 .like.active :global(svg path) {
    fill: red;
    fill-opacity: 1;
  }

  .search-card-content .description {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    color: #818181;
    font-weight: 400;
    font-size: 12px;
    font-style: normal;
    line-height: normal;
  }

  .search-card-content .description :global(svg) {
    margin-right: 10px;
  }

  .search-card-content .description p {
    color: #818181;
    font-weight: 400;
    font-size: 12px;
    font-style: normal;
    line-height: 20px;
  }

  .rating {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    color: #818181;
    font-weight: 400;
    font-size: 12px;
    font-style: normal;
    line-height: 20px;
  }

  .rating span {
    display: flex;
    align-items: center;
    margin-right: 8px;
    padding-right: 8px;
    border-right: 1px solid #e3e3e3;
  }

  .rating span :global(svg) {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 22px;
    min-height: 22px;
    margin-right: 2px;
  }

  .rating .rating-value {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 36px;
    margin-right: 8px;
    padding: 4px 8px;
    color: #ffffff;
    font-weight: 500;
    font-size: 12px;
    font-style: normal;
    line-height: normal;
    background: #94bf00;
    border-radius: 8px;
  }

  .facilities {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 16px;
    padding: 0 0 9px;
    list-style: none;
    border-bottom: 1px solid #e4e6e9;
  }

  .facilities li {
    display: flex;
    align-items: center;
    margin-right: 16px;
    color: #1c1c1c;
    font-weight: 400;
    font-size: 12px;
    font-style: normal;
    line-height: 20px;
    white-space: nowrap;
  }

  .facilities li :global(svg) {
    margin-right: 7px;
  }

  .facilities li:last-child {
    margin: 0;
  }

  .board-types {
    display: flex;
    flex-flow: column wrap;
    align-items: flex-start;
    justify-content: flex-start;
    height: 42px;
    padding: 0;
    list-style: none;
  }

  .board-types li {
    display: flex;
    align-items: center;
    color: #1c1c1c;
    font-weight: 500;
    font-size: 12px;
    font-style: normal;
    line-height: normal;
  }

  .board-types li :global(svg) {
    margin-right: 8px;
  }

  .board-types li:nth-child(odd) {
    margin-bottom: 10px;
  }

  .search-card-action {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    width: 189px;
    padding: 24px;
    position: relative;
  }

  .features {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100px;
    height: 37px;
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='38' viewBox='0 0 100 38' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill-rule='evenodd' clip-rule='evenodd' d='M0 0C3.62479 1.73638 6.30027 7.7939 6.30027 14.9999C6.30027 14.7698 6.303 14.5408 6.3084 14.313L6.3084 29.9999C6.3084 34.4182 9.89012 37.9999 14.3084 37.9999L85.7074 37.9999C90.1257 37.9999 93.7074 34.4182 93.7074 30V14.3147C93.8708 7.4122 96.4903 1.68097 99.9997 0H0Z' fill='%23E3F2F8'/%3E%3C/svg%3E%0A");
    background-repeat: no-repeat;
  }

  .features :global(svg:not(:last-child)) {
    margin-right: 8px;
  }

  .search-card-action p {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    margin-bottom: 16px;
    color: #818181;
    font-weight: 400;
    font-size: 14px;
    font-style: normal;
    line-height: 24px;
    text-align: right;
  }

  .search-card-action p span {
    padding: 0 5px;
    color: #ea7121;
    font-weight: 700;
    font-size: 28px;
    font-style: normal;
    line-height: 35px;
  }

  .search-card-action a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 12px 28px;
    color: #f7fbff;
    font-weight: 600;
    font-size: 14px;
    font-style: normal;
    line-height: normal;
    text-decoration: none;
    background-color: #ea7121;
    border-radius: 4px;
  }

  .search-card-action a:hover {
    background-color: #c45d1b;
    transition: background-color 0.3s ease-in-out;
  }
</style>
