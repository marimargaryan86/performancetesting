<script lang="ts">
  import Summary from "../passenger-details/summary.svelte";
  import BookingSteps from "../booking-steps.svelte";
  import TextField from "components/ui/text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import RadioIcon from "components/icons/radio-icon.svelte";
  import CreditCardIcon from "components/icons/credit-card-icon.svelte";
  import { onMount } from "svelte";
  import OffersMockup from "../offers-mockup";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import type { OfferModel } from "../select-offer/offer.svelte";

  const currentBookingStep = 4;
  const countries = ["Spain", "Portugal", "France", "Andorra", "Gibraltar", "Morocco"];

  let offer: OfferModel | undefined = undefined;
  let fare: OfferModel["alternativeFares"][number] | undefined = undefined;

  onMount(() => {
    const urlParams = $page.url.searchParams;

    offer = OffersMockup.find((item) => item.id === Number(urlParams.get("offer_id")));
    fare = offer?.alternativeFares.find((item) => item.id === Number(urlParams.get("fare_id")));
  });

  function goToPassengerDetailsPage(): void {
    goto(routeConfig.book.passengerDetails.root + $page.url.search);
  }
  function goToConfirmationPage(): void {
    const additionalInfo = {
      alert: { type: "success", message: "We will send an email with a copy of your ticket." },
    };
    goto(routeConfig.book.confirmation.root + $page.url.search, { state: additionalInfo });
  }
</script>

<svelte:head>
  <title>Payment · Junction Hub</title>
</svelte:head>

<h1 class="typography headline-medium bold container header">Payment</h1>
<BookingSteps currentStep={currentBookingStep} />

<div class="background">
  <div class="page-wrapper container">
    <div class="forms">
      <div class="card-form">
        <h3>Payment method</h3>
        <div class="pay-card">
          <TextField readonly value="Credit Card" />
          <RadioIcon color="var(--color-main-primary-500)" />
          <div class="card-icon">
            <CreditCardIcon />
          </div>
        </div>
        <TextField label="Card number" placeholder="4444 4444 4444 4444" required />
        <div class="row">
          <TextField label="Expiration date" placeholder="mm/yy" required />
          <TextField label="CVC" placeholder="Required" required />
        </div>
        <div class="row">
          <SelectField label="Country" placeholder="Select" options={countries} required />
          <TextField label="Postcode" placeholder="Required" required />
        </div>
      </div>
      <div class="billing-address-form">
        <h3>Billing address</h3>
        <TextField label="Address line 1" placeholder="Required" required />
        <TextField label="Address line 2" />
        <div class="location">
          <TextField class="city" placeholder="Málaga" label="Town / City" required />
          <SelectField label="Country" required scroll placeholder="Select" options={countries} />
          <TextField
            class="post-code"
            type="text"
            placeholder="Postcode"
            label="Postcode"
            required
          />
        </div>
      </div>
    </div>

    {#if offer && fare}
      <Summary {offer} {fare} />
    {/if}
  </div>

  <div class="next-block">
    <Button on:click={goToPassengerDetailsPage} size="medium" variant="outline">Previous</Button>
    <Button on:click={goToConfirmationPage} size="medium"><span class="next-btn">Pay</span></Button>
  </div>
</div>

<style>
  h3 {
    margin-bottom: 16px;
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .background {
    padding-top: 24px;
    background: var(--color-gradient-booking-flow);
  }

  .page-wrapper {
    position: relative;
    display: flex;
    flex-direction: row;
    gap: 16px;
    align-items: flex-start;
    justify-content: space-between;
    padding-bottom: 24px;
  }

  .container {
    margin: 0 24px;
  }

  .header {
    padding-top: 16px;
  }

  .card-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .forms {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    padding-bottom: 60px;
  }

  .row {
    display: flex;
    flex-direction: row;
    gap: 24px;
  }

  .forms :global(.text-field) {
    width: 100%;
  }

  .forms :global(.select-field) {
    width: 100%;
  }

  .forms :global(.text-field .wrapper) {
    height: 40px;
  }

  .forms :global(.select-field .wrapper) {
    height: 40px;
  }

  .forms :global(.select-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .forms :global(.text-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .pay-card {
    position: relative;
    width: 50%;
    min-width: 165px;
  }

  .pay-card > :global(svg) {
    position: absolute;
    top: 10px;
    left: 16px;
  }

  .pay-card .card-icon :global(svg) {
    position: absolute;
    top: 8px;
    right: 16px;
  }

  .billing-address-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .location {
    display: flex;
    flex-direction: row;
    gap: 24px;
    width: 100%;
  }

  .forms :global(.text-field.post-code) {
    max-width: 112px;
  }

  .next-block {
    position: sticky;
    bottom: 0;
    z-index: 100;
    display: flex;
    gap: 16px;
    justify-content: space-between;
    width: 100%;
    padding: 16px 24px;
    background-color: var(--color-common-dark-strong);
  }

  .next-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100px;
  }
</style>
