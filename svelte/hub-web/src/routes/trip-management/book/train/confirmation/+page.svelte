<script lang="ts" context="module">
  function getAlertType(status: CommonSchemas.OrderBookingStatus): AlertType {
    if (status === "confirmed") {
      return "success";
    } else if (status === "error" || status === "cancelled" || status === "rejected") {
      return "error";
    }

    return "warning";
  }
</script>

<script lang="ts">
  import routeConfig from "$lib/route-config";
  import Alert from "$lib/components/ui/alert.svelte";
  import type { AlertType } from "$lib/models/ui";
  import Passengers from "$lib/components/pages/trip-management/booking-flow-train/passengers.svelte";
  import Price from "$lib/components/pages/trip-management/booking-flow-train/price.svelte";
  import Overview from "$lib/components/pages/trip-management/booking-flow-train/confirmation/overview.svelte";
  import Itinerary from "$lib/components/pages/trip-management/booking-flow-train/itinerary.svelte";
  import { ensureDefined } from "$lib/utils/array";
  import * as CommonSchemas from "~/integration/common/schemas";
  import Fees from "$lib/components/pages/trip-management/booking-flow-train/confirmation/fees.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";

  export let data;

  const t = getTranslator();

  $: hasTickets = Boolean(
    data.order.bookings.flatMap((item) => item.ticketUrls).filter(ensureDefined).length,
  );
  $: orderStatus = CommonSchemas.getOrderStatus.booking(data.order);
  $: alertType = orderStatus ? getAlertType(orderStatus) : "warning";
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.book.title"),
      $t("pages.tripManagement.pages.book.pages.confirmation.title"),
    )}
  </title>
</svelte:head>

<div class="content">
  <Alert type={alertType}>
    {#if alertType === "success"}
      <span class="icon success">
        <Icon variant="checked" size="16px" color="var(--color-common-dark-strong)" />
      </span>
      <span typography="body-medium" weight="bold">{$t("words.success")}</span>
      <span typography="body-medium">{$t("sentences.theOrderWasCreatedSuccessfully")}</span>
    {:else if alertType === "error"}
      <span class="icon error">
        <Icon color="var(--color-common-dark-strong)" variant="close" />
      </span>
      <span typography="body-medium" weight="bold">{$t("words.error")}</span>
      <span typography="body-medium">{$t("sentences.theOrderWasCreatedWithErrors")}</span>
    {:else}
      <Icon variant="alert-triangle" color="var(--color-semantic-warning-600)" />
      <span typography="body-medium" weight="bold">{$t("words.warning")}</span>
      <span typography="body-medium">{$t("sentences.theOrderIsInAPendingState")}</span>
    {/if}
  </Alert>

  <div class="scroll">
    <div class="wrapper">
      <div class="details">
        <Overview order={data.order} />

        {#if hasTickets}
          <a
            variant="primary"
            href={routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id).routes
              .tickets.root}
            download
          >
            {$t("actions.downloadTickets")}
          </a>
        {/if}

        <Price bookings={data.order.bookings} />

        {#if data.markups}
          <Fees markups={data.markups} />
        {/if}

        <Passengers passengers={data.order.passengers} />

        <Itinerary bookings={data.order.bookings} />
      </div>
    </div>
  </div>
</div>

<div class="actions">
  <div class="wrapper">
    <a
      variant="primary"
      size="small"
      href={routeConfig.routes.tripManagement.routes.book.routes.train.root}
    >
      {$t("sentences.newSearch")}
    </a>
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

  .actions > .wrapper > a {
    width: 140px;
  }
</style>
