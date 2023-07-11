<script lang="ts">
  import SearchIcon from "components/icons/book-search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker from "./passenger-picker/passenger-picker.svelte";
  import SelectCityOrStation from "./select-city-or-station.svelte";
  import BookingSteps from "./booking-steps.svelte";

  const currentBookingStep = 1;

  let origin = null;
  let destination = null;
  let selectedDate = undefined;
  let adults = 0;
  let children = 0;
  let infants = 0;
</script>

<svelte:head>
  <title>Book · Junction Hub</title>
</svelte:head>

<div class="book typography body-large">
  <h1 class="typography headline-medium bold container header">Search for offers</h1>

  <BookingSteps currentStep={currentBookingStep} />

  <div class="background">
    <div class="form-wrapper">
      <div class="search-offers">
        <SelectCityOrStation bind:value={origin} direction="From" />
        <SelectCityOrStation bind:value={destination} direction="To" />
        <div class="input-wrapper">
          <label for="depart-date">Depart <span class="required-fields">*</span></label>
          <DatePicker bind:value={selectedDate} id="depart-date" placeholder="Add date" />
        </div>
        <div class="search-btn">
          <svelte:component this={SearchIcon} color="var(--color-common-dark-strong)" />
        </div>
      </div>
      <div class="passenger-select">
        <PassengerPicker bind:adults bind:children bind:infants />
      </div>
    </div>
  </div>
</div>

<style>
  .input-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-right: 8px;
  }

  .book {
    align-self: center;
    width: 100%;
    max-width: 1440px;
    height: 100%;
    border-bottom-width: 0;
    border-radius: 16px 16px 0 0;
  }

  .background {
    height: 100%;
    padding-top: 24px;
    background: var(--color-gradient-booking-flow);
  }

  .form-wrapper {
    margin: 0 24px;
    padding: 24px 24px 16px;
    background: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .container {
    margin: 0 24px;
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
    min-height: 52px;
    background-color: var(--color-main-primary-500);
    border-radius: 8px;
    cursor: pointer;
  }

  .search-btn:hover {
    background-color: var(--color-main-primary-600);
  }

  .search-offers {
    display: flex;
    align-items: flex-end;
  }

  .header {
    padding-top: 16px;
  }

  h1 {
    margin-bottom: 16px;
  }
</style>
