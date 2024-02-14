<script lang="ts">
  import FaPlane from "svelte-icons/fa/FaPlane.svelte";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";
  import FaHotel from "svelte-icons/fa/FaHotel.svelte";
  export let destination: string;

  let places = [
    {
      name: "London Heathrow",
      country: "United Kingdom",
      type: "airport",
      id: "LHR",
    },
    {
      name: "Eiffel Tower",
      country: "France",
      type: "landmark",
      id: "EFT",
    },
    {
      name: "Dubai International Airport",
      country: "UAE",
      type: "airport",
      id: "DXB",
    },
    {
      name: "Sydney Opera House",
      country: "Australia",
      type: "landmark",
      id: "SOH",
    },
    {
      name: "Los Angeles International Airport",
      country: "America",
      type: "airport",
      id: "LAX",
    },
    {
      name: "Statue of Liberty",
      country: "America",
      type: "landmark",
      id: "SOL",
    },
    {
      name: "Haneda Airport",
      country: "Japan",
      type: "airport",
      id: "HND",
    },
    {
      name: "Mount Fuji",
      country: "Japan",
      type: "landmark",
      id: "MFJ",
    },
  ];

  $: placeNamesContainingDestinations = places.filter((place) =>
    place.name.toLowerCase().includes(destination.toLowerCase()),
  );
</script>

<div class="dropdown">
  <ul>
    {#each placeNamesContainingDestinations as place}
      <label class="place-label" for={place.id}>
        <div class="icon">
          {#if place.type === "airport"}
            <FaPlane />
          {:else if place.type === "landmark"}
            <FaMapMarkerAlt />
          {:else if place.type === "hotel"}
            <FaHotel />
          {/if}
        </div>
        <input
          id={place.id}
          type="radio"
          class="destination-option"
          value={place.id}
          bind:group={destination}
          hidden
        />
        <p class="destination-label">{place.name}</p>
      </label>
    {/each}
  </ul>
</div>

<style>
  .dropdown {
    position: absolute;
    box-shadow: 0px 0px 29.7px 0px rgba(0, 0, 0, 0.1);
    background: #fff;
    top: 110px;
    display: flex;
    flex-direction: column;
    left: -36px;
    width: 150%;
    padding: 16px 10px;
  }

  .place-label {
    display: flex;
    align-items: center;
    border-bottom: 1px solid #f2f2f2;
    gap: 10px;
  }
  .icon {
    width: 16px;
  }
</style>
