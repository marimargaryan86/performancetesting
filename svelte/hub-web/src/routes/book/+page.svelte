<script lang="ts">
  import BookingSteps from "./booking-steps.svelte";
  import SearchForm from "./search-form.svelte";

  const currentBookingStep = 1;
</script>

<svelte:head>
  <title>Book · Junction Hub</title>
</svelte:head>

<div class="book typography body-large">
  <h1 class="typography headline-medium bold container header">Search for offers</h1>

  <BookingSteps currentStep={currentBookingStep} />

  <div class="background">
    <SearchForm firstStep={currentBookingStep === 1} />
  </div>
</div>

<style>
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

  .container {
    margin: 0 24px;
  }

  .header {
    padding-top: 16px;
  }

  h1 {
    margin-bottom: 16px;
  }
</style>
