<script lang="ts">
  import TicketInCircle from "components/icons/ticket-in-circle-icon.svelte";
  import CheckInCircle from "components/icons/check-in-circle-icon.svelte";
  import UserInCircle from "components/icons/user-in-circle-icon.svelte";
  import ClockInCircle from "components/icons/clock-in-circle-icon.svelte";
  import ChairInCircle from "components/icons/chair-in-circle-icon.svelte";
  import Button from "components/ui/button.svelte";
  import { goto } from "$app/navigation";
  import routeConfig from "routeConfig";
  import Alert from "components/ui/alert.svelte";
  import PaymentModal from "../payment/payment-modal.svelte";
  import { onMount } from "svelte";

  let alert: { type: "success" | "failed"; message: string } | undefined = {
    type: "success",
    message: "We will send an email with a copy of your ticket.",
  };
  let showPaymentSucceed = true;

  function goToBookingsPage(): void {
    const additionalInfo = { alert: { type: "success", message: "Booking successfully made" } };
    goto(routeConfig.go.bookings.root, { state: additionalInfo });
  }

  onMount(() => {
    setTimeout(() => {
      showPaymentSucceed = false;
    }, 2000);
  });

  function closeAlert(): void {
    alert = undefined;
  }
</script>

<svelte:head>
  <title>Confirmation · Junction Hub</title>
</svelte:head>

<h1 class="typography headline-medium bold container header">Confirmation</h1>

<div class="background">
  {#if alert}
    <div class="container">
      <Alert on:close={closeAlert} type={alert.type}>{alert.message}</Alert>
    </div>
  {/if}
  <div class="page-wrapper container typography body-medium" class:alert>
    <div class="booking">
      <div class="congratulation">
        <span class="typography body-small">Congratulations!</span>
        <h2 class="typography headline-small bold">Your booking has been confirmed</h2>
        <div class="number-status">
          <div class="booking-number">
            <TicketInCircle color="var(--color-main-primary-500)" />
            <div class="column">
              <span class="typography body-xsmall">Reservation number</span>
              <span class="typography title-small bold">J98PLK17</span>
            </div>
          </div>
          <div class="booking-status">
            <CheckInCircle color="var(--color-main-primary-500)" />
            <div class="column">
              <span class="typography body-xsmall">Status</span>
              <span class="typography title-small bold">Confirmed</span>
            </div>
          </div>
        </div>
      </div>
      <div class="view-ticket">
        <Button on:click={goToBookingsPage}>View ticket in bookings</Button>
      </div>
      <div class="prices typography body-small">
        <span>The price is for all passengers</span>
        <div class="price-row">
          <span>Base far</span>
          <span class="typography bold">€80.00</span>
        </div>
        <div class="price-row">
          <span>Taxes</span>
          <span class="typography bold">€10.00</span>
        </div>
        <div class="price-row">
          <span>Fees</span>
          <span class="typography bold">€10.00</span>
        </div>
        <div class="price-row">
          <span>Agency mark-up</span>
          <span class="typography bold">€2.50</span>
        </div>
        <div class="price-row">
          <span>Contractual mark-up</span>
          <span class="typography bold">€2.50</span>
        </div>
        <div class="price-row total-price typography title-medium bold">
          <span>Total to pay</span>
          <span class="typography bold">€149.00</span>
        </div>
      </div>
      <div class="passenger-details">
        <h3 class="typography body-large bold">Passenger details</h3>
        <div class="passenger">
          <UserInCircle color="var(--color-main-primary-500)" />
          <span class="typography body-small-weight-600">Jerry Smith</span>
          <span class="typography body-small">Adult 1</span>
        </div>
        <div class="passenger">
          <UserInCircle color="var(--color-main-primary-500)" />
          <span class="typography body-small-weight-600">Beth Smith</span>
          <span class="typography body-small">Adult 2</span>
        </div>
      </div>
      <div class="itinerary-details">
        <h3 class="typography body-large bold">Itinerary details</h3>
        <div class="outbound-date">
          <span>Outbound</span>
          <span>1st Jul</span>
        </div>
        <div class="origin-destination">
          <span class="typography title-medium">Malaga Maria Zambrano</span>
          <span>to</span>
          <span class="typography title-medium">Barcelona Sants</span>
        </div>
        <div class="offer-preview typography body-small">
          <img src="/images/renfe-logo.png" width="26" height="26" alt="logo" />
          <span>Renfe • AVE 2123 • Direct • Standard</span>
        </div>
        <div class="departure-arrival typography">
          <div class="departure">
            <span>Departure</span>
            <span class="typography body-xlarge bold">8:50</span>
          </div>
          <div class="arrival">
            <span>Arrival</span>
            <span class="typography body-xlarge bold">9:30</span>
          </div>
        </div>
        <div class="additional-info">
          <div class="trip-duration">
            <ClockInCircle color="var(--color-main-primary-500)" />
            <div class="column">
              <span class="typography body-xsmall">Trip duration</span>
              <span class="typography title-small bold">1h 40m</span>
            </div>
          </div>
          <div class="fare-class">
            <ChairInCircle color="var(--color-main-primary-500)" />
            <div class="column">
              <span class="typography body-xsmall">Fare class</span>
              <span class="typography title-small bold">Standard Flex</span>
            </div>
          </div>
        </div>
        <div class="fare-rule">
          <span>Fare rule</span>
        </div>
      </div>
    </div>
  </div>
</div>
<div class="next-block">
  <Button size="medium" on:click={goToBookingsPage}><span class="next-btn">Next</span></Button>
</div>

{#if showPaymentSucceed}
  <PaymentModal paymentSucceed />
{/if}

<style>
  .background {
    padding: 24px 0;
    overflow: hidden;
    background: var(--color-gradient-booking-flow);
  }

  h2 {
    padding-bottom: 26px;
  }

  .container {
    margin: 0 24px;
  }

  .header {
    padding-top: 16px;
  }

  .page-wrapper {
    display: flex;
    justify-content: center;
    height: 100%;
    overflow: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .booking {
    display: flex;
    flex-direction: column;
    gap: 40px;
    width: 432px;
    padding: 32px 0;
  }

  .number-status,
  .additional-info {
    display: flex;
    flex-direction: row;
    gap: 26px;
    width: 100%;
  }

  .column {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 4px 0;
  }

  .column > :first-child {
    color: var(--color-main-primary-700);
  }

  .booking-number,
  .booking-status,
  .trip-duration,
  .fare-class {
    display: flex;
    flex-direction: row;
    gap: 8px;
    justify-content: flex-start;
    width: 50%;
  }

  .congratulation {
    padding-bottom: 4px;
  }

  .view-ticket {
    display: flex;
    justify-content: center;
  }

  .prices {
    display: flex;
    flex-direction: column;
  }

  .prices > :first-child {
    padding-bottom: 16px;
  }

  .price-row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding-bottom: 4px;
  }

  .total-price {
    margin-top: 16px;
  }

  .total-price > :last-child {
    color: var(--color-main-primary-500);
  }

  .passenger {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
    padding: 16px;
    border: 0.5px solid var(--color-main-primary-500);
    border-radius: 8px;
  }

  .passenger > :global(svg) {
    padding-right: 8px;
  }

  .passenger > :last-child {
    padding-left: 16px;
    color: var(--color-main-neutral-600);
  }

  .passenger-details {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .outbound-date {
    display: flex;
    flex-direction: row;
    gap: 16px;
    margin-top: 32px;
    margin-bottom: 8px;
  }

  .origin-destination {
    margin-bottom: 24px;
  }

  .offer-preview {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 24px;
  }

  .departure-arrival {
    display: flex;
    flex-direction: row;
    width: 100%;
    padding: 16px 0;
  }

  .departure,
  .arrival {
    display: flex;
    flex-direction: column;
    width: 50%;
  }

  .departure > :first-child,
  .arrival > :first-child {
    color: var(--color-main-neutral-600);
  }

  .fare-rule {
    position: relative;
    display: flex;
    justify-content: flex-end;
    padding: 20px 0 32px;
  }

  .next-block {
    position: sticky;
    bottom: 0;
    display: flex;
    gap: 16px;
    align-items: flex-end;
    align-self: stretch;
    justify-content: end;
    width: 100%;
    padding: 16px 24px;
    background-color: var(--color-common-dark-strong);
  }

  .fare-rule :global(.dialogue) {
    top: -70px;
    right: 0;
  }

  .alert {
    height: calc(100% - 78px);
  }
</style>
