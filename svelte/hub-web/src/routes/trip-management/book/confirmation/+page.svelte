<script lang="ts" context="module">
  function getAlertType(status: OrderModel["status"]): AlertType {
    if (status === "confirmed") {
      return "success";
    } else if (status === "error" || status === "cancelled" || status === "rejected") {
      return "error";
    }

    return "warning";
  }
</script>

<script lang="ts">
  import Button from "components/ui/button.svelte";
  import routeConfig from "routeConfig";
  import Alert, { type AlertType } from "components/ui/alert.svelte";
  import CheckedIcon from "components/icons/checked-icon.svelte";
  import Passengers from "../../components/passengers.svelte";
  import Price from "./price.svelte";
  import Overview from "./overview.svelte";
  import Itinerary from "../../components/itinerary.svelte";
  import { ensureDefined } from "utils/array";
  import { downloadTickets } from "utils/booking";
  import CloseIcon from "components/icons/close-icon.svelte";
  import AlertIcon from "components/icons/alert-icon.svelte";
  import type { OrderModel } from "integration/junction-mobile-api/schemas/order";

  export let data;

  $: hasTickets = Boolean(
    data.order.bookings.map((item) => item.ticketUrl).filter(ensureDefined).length,
  );
  $: alertType = getAlertType(data.order.status);
</script>

<svelte:head>
  <title>Confirmation · Trip Management · Junction Hub</title>
</svelte:head>

<div style:display="none">
  {JSON.stringify(data.order)}
</div>

<div class="content">
  <Alert type={alertType}>
    {#if alertType === "success"}
      <span class="icon success">
        <CheckedIcon color="var(--color-common-dark-strong)" />
      </span>
      <span class="typography body-medium bold">Success</span>
      <span class="typography body-medium">The order was created successfully</span>
    {:else if alertType === "error"}
      <span class="icon error">
        <CloseIcon color="var(--color-common-dark-strong)" variant="cross" />
      </span>
      <span class="typography body-medium bold">Error</span>
      <span class="typography body-medium">The order was created with errors</span>
    {:else}
      <AlertIcon color="var(--color-semantic-warning-600)" />
      <span class="typography body-medium bold">Warning</span>
      <span class="typography body-medium">The order is in a pending state</span>
    {/if}
  </Alert>

  <div class="scroll">
    <div class="wrapper">
      <div class="details">
        <Overview order={data.order} />

        {#if hasTickets}
          <Button on:click={downloadTickets.bind(downloadTickets, data.order.bookings)}>
            Download tickets
          </Button>
        {/if}

        <Price bookings={data.order.bookings} />

        <Passengers passengers={data.order.passengers} />

        <Itinerary bookings={data.order.bookings} />
      </div>
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <Button size="small" href={routeConfig.routes.tripManagement.routes.book.root}
      >New search</Button
    >
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

  .icon {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
  }

  .icon.success {
    background-color: var(--color-semantic-success-600);
  }

  .icon.error {
    background-color: var(--color-semantic-error-600);
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
