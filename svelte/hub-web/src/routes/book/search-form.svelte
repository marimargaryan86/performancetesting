<script lang="ts">
  import SearchIcon from "components/icons/book-search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker from "./passenger-picker/passenger-picker.svelte";
  import SelectCityOrStation from "./select-city-or-station.svelte";
  import type { BookingSearchForm } from "./booking-search-form";
  import routeConfig from "routeConfig";

  export let firstStep = true;

  export let bookingSearchForm: BookingSearchForm = {
    origin: "",
    destination: "",
    fromDate: undefined,
    adults: 0,
    children: 0,
    infants: 0,
  };

  $: searchQuery = `?origin=${bookingSearchForm.origin}&destination=${
    bookingSearchForm.destination
  }&from=${new Date(bookingSearchForm.fromDate).getTime()}&adults=${
    bookingSearchForm.adults
  }&children=${bookingSearchForm.children}&infants=${bookingSearchForm.infants}`;

  function search(): void {
    if (isSearchParametersValid()) {
      location.href = routeConfig.book.select.root + searchQuery;
    }
  }

  function isSearchParametersValid(): boolean {
    let valid = true;

    if (
      !bookingSearchForm.origin ||
      !bookingSearchForm.destination ||
      !bookingSearchForm.fromDate ||
      bookingSearchForm.adults < 1
    ) {
      valid = false;
    }

    return valid;
  }
</script>

<div class="form-wrapper {firstStep ? '' : 'unset-margin'}">
  <div class="search-offers">
    <SelectCityOrStation bind:value={bookingSearchForm.origin} direction="From" {firstStep} />
    <SelectCityOrStation bind:value={bookingSearchForm.destination} direction="To" {firstStep} />
    <div class="input-wrapper" class:select-date={!firstStep}>
      <label for="depart-date" class={firstStep ? "" : "typography body-small"}
        >Depart <span class="required-fields">{firstStep ? "*" : ""}</span></label
      >
      <DatePicker bind:value={bookingSearchForm.fromDate} id="depart-date" placeholder="Add date" />
    </div>
    <div class="search-btn {firstStep ? 'first-step-search-btn' : ''}" on:click={search}>
      <svelte:component this={SearchIcon} color="var(--color-common-dark-strong)" />
    </div>
  </div>
  <div class="passenger-select">
    <PassengerPicker
      bind:adults={bookingSearchForm.adults}
      bind:children={bookingSearchForm.children}
      bind:infants={bookingSearchForm.infants}
    />
  </div>
</div>

<style>
  .input-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 100%;
    margin-right: 8px;
  }

  .form-wrapper.unset-margin {
    margin: unset;
    padding: 16px 24px;
    border-radius: unset;
  }

  .form-wrapper {
    margin: 0 24px;
    padding: 24px 24px 16px;
    background: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .passenger-select {
    margin-top: 16px;
  }

  .required-fields {
    color: var(--color-main-primary-500);
  }

  .search-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 52px;
    min-height: 40px;
    background-color: var(--color-main-primary-500);
    border-radius: 8px;
    cursor: pointer;
  }

  .first-step-search-btn {
    min-width: 52px;
    min-height: 52px;
  }

  .search-btn:hover {
    background-color: var(--color-main-primary-600);
  }

  .search-offers {
    display: flex;
    align-items: flex-end;
  }

  .select-date > :global(.date-picker) {
    --height: 40px;
  }

  .input-wrapper > :global(.date-picker) {
    --width: 100%;
  }
</style>
