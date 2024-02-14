<script lang="ts">
  import FaPlaneDeparture from "svelte-icons/fa/FaPlaneDeparture.svelte";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";
  import FaRegCalendarAlt from "svelte-icons/fa/FaRegCalendarAlt.svelte";
  import FaUsers from "svelte-icons/fa/FaUsers.svelte";
  import FaSearch from "svelte-icons/fa/FaSearch.svelte";
  import OriginAirportSelect from "./origin-airport-select.svelte";
  import PassengerSelectionBox from "./passenger-selection-box.svelte";
  import CalendarSelect from "./calendar-select.svelte";
  import DestinationSelect from "./destination-select.svelte";
  import RoomsSelect from "./rooms-select.svelte";

  export let searchType: string;

  let searchOptions = {
    passengers: { adults: 1, children: 0 },
  };

  let journeyType: string = "one-way";
  let origin: string = "";
  let dropdown: string = "";
  let destination: string = "";

  const setDropdown = (value: string): void => {
    if (dropdown === value) {
      dropdown = "";
    } else {
      dropdown = value;
    }
  };
  // child and children ruin it
  function pluralise(count: number, singular: string, plural: string): string {
    return count === 1 ? singular : plural;
  }
</script>

{origin}
<div class="search-panel">
  <div class="return-journey">
    <input type="radio" id="one-way" bind:group={journeyType} value="one-way" />
    <label for="one-way">One-way</label>
    <input type="radio" id="return" bind:group={journeyType} value="return" />
    <label for="return">Return</label>
  </div>
  <div class="search-container">
    <div class="search-section location-section">
      <div class="label">
        <div class="label-container">
          <div class="icon">
            <FaPlaneDeparture />
          </div>
          <p class="label">Origin</p>
        </div>
        <input
          class="location-input"
          bind:value={origin}
          placeholder="Flying from"
          on:focusin={setDropdown.bind(setDropdown, "location")}
        />
      </div>
    </div>
    <!-- Change to new way with styles -->
    {#if dropdown === "location"}
      <OriginAirportSelect />
    {/if}
    <div class="search-section departure-section">
      <div class="label">
        <div class="label-container">
          <div class="icon">
            <FaMapMarkerAlt />
          </div>
          <p class="label">Destination</p>
        </div>
        <input
          class="location-input"
          placeholder="Flying to"
          on:focusin={setDropdown.bind(setDropdown, "destination")}
          bind:value={destination}
        />
      </div>
      {#if dropdown === "destination"}
        <DestinationSelect {destination} />
      {/if}
    </div>
    <div class="search-section date-section">
      <button class="label date-label" on:click={setDropdown.bind(setDropdown, "date")}>
        <div class="label-container">
          <div class="icon">
            <FaRegCalendarAlt />
          </div>
          <p class="label">Date</p>
        </div>
        <p class="desc">Select your date</p>
      </button>
      {#if dropdown === "date"}
        <CalendarSelect returnTrip={journeyType === "return"} />
      {/if}
    </div>
    <div class="search-section people-section" class:border={searchType !== "flights"}>
      <button class="label people-label" on:click={setDropdown.bind(setDropdown, "people")}>
        <div class="label-container">
          <div class="icon">
            <FaUsers />
          </div>
          <p class="label">Passengers</p>
        </div>
        <p class="desc">
          {searchOptions.passengers.adults}
          {pluralise(searchOptions.passengers.adults, "adult", "adults")}
          {#if searchOptions.passengers.children > 0}
            and {searchOptions.passengers.children}
            {pluralise(searchOptions.passengers.children, "child", "children")}
          {/if}
        </p>
      </button>
      {#if dropdown === "people"}
        <PassengerSelectionBox bind:passengers={searchOptions.passengers} />
      {/if}
    </div>

    {#if searchType === "hotels" || searchType === "combo"}
      <div class="search-section hotel-section">
        <button class="label hotel-label" on:click={setDropdown.bind(setDropdown, "hotels")}>
          <div class="label-container">
            <div class="icon">
              <FaUsers />
            </div>
            <p class="label">Rooms & Guests</p>
          </div>
          <p class="desc">Select Guests</p>
        </button>
        {#if dropdown === "hotels"}
          <RoomsSelect />
        {/if}
      </div>
    {/if}
    <div class="search-section search">
      <button class="booking-search"
        ><div class="icon"><FaSearch /></div>
        Search</button
      >
    </div>
  </div>
</div>

<style>
  .search-panel {
    display: flex;
    flex-direction: column;
    padding: 20px 25px 35px;
    background-color: #ffffff;
    border-radius: 0 10px 10px;
  }

  .return-journey {
    display: flex;
    margin: 15px 0 30px;
  }

  .return-journey label {
    margin-right: 15px;
    margin-left: 7.5px;
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
  }

  .search-container {
    position: relative;
    display: flex;
    flex: 1;
    gap: 20px;
  }

  .label {
    color: #1c1c1c;
    font-weight: 500;
    font-size: 16px;
  }

  .search-section {
    position: relative;
    display: flex;
    flex-basis: 22.5%;
    gap: 30px;
    align-items: center;
    margin: 0 10px;
    margin-bottom: 12px;
    border-right: 1px solid #1c1c1c;
  }

  .search-section:last-child {
    flex-basis: 10%;
    border-right: none;
  }

  .search-section > .label {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .people-section,
  .hotel-section {
    border: none;
  }

  .icon {
    width: 18px;
    height: 18px;
    color: #1c1b1f;
  }

  .label-container {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .label p {
    margin: 0;
  }

  .location-input {
    width: 90%;
    padding: 8px 0;
    color: #1c1c1c;
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    border: none;
  }

  .desc {
    color: #1c1c1c;
    color: var(--text-grey-text, #818181);
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: 25px;
    line-height: normal;
    opacity: 0.5;
  }

  .booking-search {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 16px 22px;
    color: white;
    font-size: 16px;
    background: var(--text-dark-text, #1c1c1c);
    border: none;
    border-radius: 2px;
  }

  .border {
    border-right: 1px solid #1c1c1c;
  }

  .booking-search > .icon {
    width: 18px;
    color: white;
  }

  button.label:hover {
    cursor: pointer;
  }

  .people-label,
  .hotel-label,
  .date-label {
    background: none;
    border: none;
  }
</style>
