<script lang="ts">
  import FaPlaneDeparture from "svelte-icons/fa/FaPlaneDeparture.svelte";
  import FaMapMarkerAlt from "svelte-icons/fa/FaMapMarkerAlt.svelte";
  import FaRegCalendarAlt from "svelte-icons/fa/FaRegCalendarAlt.svelte";
  import FaUsers from "svelte-icons/fa/FaUsers.svelte";
  import FaSearch from "svelte-icons/fa/FaSearch.svelte";
  import OriginAirportSelect from "./components/origin-airport-select.svelte";
  import PassengerSelectionBox from "./components/passenger-selection-box.svelte";
  import CalendarSelect from "./components/calendar-select.svelte";
  import DestinationSelect from "./components/destination-select.svelte";
  import RoomsSelect from "./components/rooms-select.svelte";

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
    background-color: #ffffff;
    border-radius: 10px;
    padding: 20px 25px 35px;
    display: flex;
    flex-direction: column;
  }
  .return-journey {
    display: flex;
    margin: 15px 0 30px;
  }
  .return-journey label {
    font-size: 16px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    margin-left: 7.5px;
    margin-right: 15px;
  }
  .search-container {
    position: relative;
    display: flex;
    gap: 20px;
    flex: 1;
  }
  .search-section {
    display: flex;
    gap: 30px;
    margin-bottom: 12px;
    align-items: center;
    border-right: 1px solid #1c1c1c;
    margin: 0 10px;
    flex-basis: 22.5%;
    position: relative;
  }
  .search-section:last-child {
    border-right: none;
    flex-basis: 10%;
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
  .label {
    font-weight: 500;
    font-size: 16px;
    color: #1c1c1c;
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
    border: none;

    padding: 8px 0;
    font-size: 16px;
    color: #1c1c1c;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
    width: 90%;
  }
  .desc {
    font-size: 16px;
    color: #1c1c1c;
    opacity: 0.5;
    line-height: 25px;
    color: var(--Text-Grey-Text, #818181);
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }
  .booking-search {
    background: var(--Text-Dark-Text, #1c1c1c);
    color: white;
    border: none;
    border-radius: 2px;
    padding: 16px 22px;
    font-size: 16px;
    display: flex;
    gap: 4px;
    align-items: center;
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
    border: none;
    background: none;
  }
</style>
