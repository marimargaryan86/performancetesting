<script lang="ts">
  import Icon from "../../components/icon.svelte";
  import type { SearchOptions } from "$lib/models/common";
  import {
    DEFAULT_SEARCH_OPTIONS,
    DEFAULT_SUPPORT_TELEPHONE_NUMBER,
    formatOriginDestination,
    formatDates,
    formatPassengersAndRooms,
  } from "$lib/helpers/search-header";
  import Container from "$lib/components/container.svelte";
  // TODO(04-24-2024/a.santos): Pull down URL query params.

  export let searchOptions: SearchOptions | undefined;

  const nextSearchOptions = {
    ...DEFAULT_SEARCH_OPTIONS,
    ...searchOptions,
  };

  $: originAndDestinationString = formatOriginDestination(nextSearchOptions, {
    useTitleCase: true,
    replaceHyphensWithSpaces: true,
  });
  $: datesString = formatDates(nextSearchOptions);
  $: passengersAndRoomsString = formatPassengersAndRooms(nextSearchOptions);
</script>

<header>
  <section class="icon">
    <a href="/" class="logo">
      <img src="/icons/bigxtra-logo.svg" alt="BigXtra logo" />
    </a>
  </section>

  <section class="search">
    <Container>
      <form class="header-search-panel" name="search-options" slot="content">
        <div class="input-wrapper">
          <label for="search-header-origin-destination">Origin-Destination</label>
          <input
            type="text"
            id="search-header-origin-destination"
            name="origin-destination"
            class="origin-destination"
            bind:value={originAndDestinationString}
          />
        </div>
        <div class="input-wrapper center">
          <label for="search-header-dates">Dates</label>
          <input
            type="text"
            id="search-header-dates"
            name="dates"
            class="dates"
            bind:value={datesString}
          />
        </div>
        <div class="input-wrapper">
          <label for="search-header-passengers-and-rooms">Passengers and Rooms</label>
          <input
            type="text"
            id="search-header-passengers-and-rooms"
            name="passengers-and-rooms"
            class="passengers-and-rooms"
            bind:value={passengersAndRoomsString}
          />
        </div>
      </form>
    </Container>
  </section>

  <section class="widget">
    <div class="icon heart-icon">
      <a href="/coming-soon" title="search-header-heart-icon">
        <Icon variant="heart-full" color="#ffffff" />
      </a>
    </div>

    <a
      data-testid="phoneLink"
      class="phone-box"
      href="tel:+089710451462"
      aria-label="Link for support phone number"
    >
      <div class="icon">
        <Icon variant="phone" color="white" />
      </div>
      {DEFAULT_SUPPORT_TELEPHONE_NUMBER}
    </a>
  </section>
</header>

<style>
  header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    height: 78px;
    background-color: var(--colours-primary-blue);
    padding: 0 68px;
  }

  .logo {
    display: flex;
    width: 100px;
  }

  .logo img {
    width: 100%;
  }

  .header-search-panel {
    display: flex;
    align-items: center;
    flex: 1;
    height: 45px;
    padding: 0 25px;
  }

  .input-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
  }

  .input-wrapper input {
    text-align: center;
    border: none;
    width: 100%;
    min-width: 192px;
  }

  .input-wrapper.center {
    padding: 0 8px;
    margin: 0 8px;
    border-right: 1px solid var(--divider-color);
    border-left: 1px solid var(--divider-color);
  }

  input,
  a {
    font-family: "Plus Jakarta Sans", var(--font-body);
    font-weight: 600;
    font-size: 16px;
    line-height: 20px;
  }

  a {
    color: var(--text-light);
  }

  a:hover {
    text-decoration: none;
  }

  input.dates {
    width: 208px;
  }

  .widget {
    display: flex;
    gap: 30px;
    align-items: center;
    width: auto;
    height: auto;
  }

  .phone-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px 18px;
    color: white;
  }

  label {
    display: none;
  }
</style>
