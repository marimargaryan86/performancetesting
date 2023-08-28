<script lang="ts">
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import Alert from "components/ui/alert.svelte";
  import CheckedIcon from "components/icons/checked-icon.svelte";
  import Passengers from "./passengers.svelte";
  import Price from "./price.svelte";
  import Overview from "./overview.svelte";
  import Itinerary from "./itinerary.svelte";

  export let data;
</script>

<svelte:head>
  <title>Confirmation · Junction Hub</title>
</svelte:head>

<div style:display="none">
  {JSON.stringify(data.order)}
</div>

<div class="content">
  <Alert type="success">
    <span class="checked-icon">
      <CheckedIcon color="var(--color-common-dark-strong)" />
    </span>
    <span class="typography body-medium bold">Success!</span>
    <span class="typography body-medium">We will send an email with a copy of your ticket.</span>
  </Alert>

  <div class="scroll">
    <div class="wrapper">
      <div class="details">
        <Overview order={data.order} />

        <Button>Download tickets</Button>

        <Price bookings={data.order.bookings} />

        <Passengers passengers={data.order.passengers} />

        <Itinerary bookings={data.order.bookings} />
      </div>
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button size="small" href={routeConfig.tripManagement.book.root}>New search</Button>
  </div>
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    width: 100%;
    padding-top: 24px;
    overflow: auto;
  }

  .content > :global(.alert) {
    max-width: 1104px;
    margin: 0 24px 24px;
  }

  .checked-icon {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    background-color: var(--color-semantic-success-600);
    border-radius: 50%;
  }

  .scroll {
    display: flex;
    flex-grow: 1;
    gap: 24px;
    width: 100%;
    padding: 0 24px 24px;
    overflow: auto;
  }

  .scroll > .wrapper {
    display: flex;
    align-self: flex-start;
    justify-content: center;
    width: 100%;
    max-width: 1104px;
    padding: 32px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .details {
    display: flex;
    flex-direction: column;
    gap: 40px;
    width: 100%;
    max-width: 432px;
    color: var(--color-main-primary-900);
  }

  .actions {
    position: relative;
    padding: 16px 24px;
    background-color: var(--color-common-background-light-main);
  }

  .actions > .wrapper {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
    width: 100%;
    max-width: 1104px;
  }

  .actions::after {
    position: absolute;
    bottom: 100%;
    left: 0;
    display: block;
    width: 100%;
    height: 10px;
    background-image: linear-gradient(0deg, rgb(0 0 0 / 0.05) 0%, rgb(0 0 0 / 0) 100%);
    content: "";
    pointer-events: none;
  }

  .actions > .wrapper > :global(button) {
    width: 140px;
  }
</style>
