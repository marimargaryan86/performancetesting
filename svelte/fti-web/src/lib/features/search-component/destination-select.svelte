<script lang="ts">
  import { places } from "$lib/data/constants";
  import Icon from "$lib/components/icon.svelte";
  export let destination: string;

  $: placeNamesContainingDestinations = places.filter((place) => place?.name?.toLowerCase());
</script>

<div class="dropdown">
  <ul>
    {#each placeNamesContainingDestinations as place}
      <label class="place-label" for={place.id}>
        <div class="icon">
          {#if place.type === "airport"}
            <Icon variant="take-off" color="#1c1b1f" size="18px" />
          {:else if place.type === "landmark"}
            <Icon variant="map-marker" color="#1c1b1f" size="18px" />
          {:else if place.type === "hotel"}
            <Icon variant="bed" color="#1c1b1f" size="18px" />
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
    top: 110px;
    left: -36px;
    display: flex;
    flex-direction: column;
    width: 150%;
    padding: 16px 10px;
    background: #ffffff;
    box-shadow: 0 0 29.7px 0 rgb(0 0 0 / 0.1);
  }

  .place-label {
    display: flex;
    gap: 10px;
    align-items: center;
    border-bottom: 1px solid #f2f2f2;
  }

  .icon {
    width: 16px;
  }

  @media only screen and (width <= 720px) {
    .dropdown {
      top: 90px;
      left: -10px;
      width: 100%;
    }
  }
</style>
