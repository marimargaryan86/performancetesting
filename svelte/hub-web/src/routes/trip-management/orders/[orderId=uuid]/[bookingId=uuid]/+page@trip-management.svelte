<script lang="ts">
  import type { BreadCrumb } from "components/page/bread-crumbs.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import routeConfig from "routeConfig";
  import { getDestination, getOrigin } from "utils/booking";
  import Passengers from "../../../components/passengers.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import Itinerary from "../../../components/itinerary.svelte";
  import StatusBadge from "components/ui/status-badge.svelte";
  import { getUser, permitted } from "utils/permissions";
  import Admin from "./admin.svelte";
  import { formatAmount } from "formatting/currency";
  import Fees from "../../../book/confirmation/fees.svelte";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";
  import Price from "../../../components/price.svelte";

  export let data;

  const locale = getLocale();
  const i18n = getLocaleData();
  const user = getUser();

  let breadCrumbs: BreadCrumb[];

  $: i18nOrders = $i18n.pages.tripManagement.pages.orders;
  $: order = data.booking.order;
  $: reservationNo = data.booking.operatorBookingReferences.length
    ? data.booking.operatorBookingReferences.join(", ")
    : undefined;
  $: bookingTitle = `${$i18n.words.booking} ${data.bookingNo}`;
  $: orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.booking.orderId);
  $: selfLink = orderLink.routes.booking(data.booking.id);
  $: breadCrumbs = [
    { label: i18nOrders.title, url: routeConfig.routes.tripManagement.routes.orders.root },
    { label: order?.journey?.reference ?? $i18n.words.unknown, url: orderLink.root },
    {
      label: bookingTitle,
      url: selfLink.root,
    },
  ];
  $: canViewTransactions = permitted($user, "transaction.view");
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.orders.title,
      order?.journey?.reference ?? "Unknown",
      bookingTitle,
    )}
  </title>
</svelte:head>

<StandardLayout {breadCrumbs}>
  <svelte:fragment slot="page-title">
    {bookingTitle}:
    <span class="typography title-large bold">
      {getOrigin(data.booking)?.name ?? $i18n.words.unknown}
      {$i18n.words.to.toLowerCase()}
      {getDestination(data.booking)?.name ?? $i18n.words.unknown}
    </span>
  </svelte:fragment>

  <div class="content" style:--grid-columns={canViewTransactions ? "1fr 1fr" : "1fr"}>
    <div class="booking">
      <div class="itinerary">
        <h3 class="typography title-large bold">{$i18n.words.itinerary}</h3>

        <Ticket identifier={reservationNo} title={$i18n.words.reservationNumber} />

        {#if order}
          <Price bookings={order.bookings} />
        {/if}

        {#if data.markups}
          <Fees markups={data.markups} />
        {/if}

        <div class="statuses">
          <div class="status typography body-small bold">
            {$i18n.words.bookingStatus}
            <StatusBadge value={data.booking.status} />
          </div>

          {#if data.booking.cancellation?.status}
            <div class="status typography body-small bold">
              {$i18n.words.cancellationStatus}
              <StatusBadge value={data.booking.cancellation.status} />
            </div>
          {/if}
        </div>
      </div>

      {#if data.booking.refund}
        <div class="refund typography body-medium bold">
          <h3 class="typography body-large bold">
            {$i18n.words.refund}

            <StatusBadge value={data.booking.refund.status} />
          </h3>
          <strong>{$i18n.words.total}</strong>
          <span>
            {data.booking.refund.refunded.reseller
              ? formatAmount(data.booking.refund.refunded.reseller, { locale: $locale, sign: true })
              : $i18n.words.notAvailable}
          </span>
        </div>
      {/if}

      {#if order}
        <Passengers passengers={order.passengers} orderCreatedAt={order.createdAt} />
      {/if}

      <Itinerary bookings={[data.booking]} />
    </div>

    {#if canViewTransactions}
      <Admin bind:booking={data.booking} />
    {/if}
  </div>
</StandardLayout>

<style>
  .content {
    display: grid;
    grid-template-columns: var(--grid-columns);
    gap: 24px;
    align-items: flex-start;
    max-width: 1152px;
  }

  .booking {
    display: flex;
    flex-flow: column;
    gap: 48px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .itinerary {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }

  .statuses {
    display: flex;
    gap: 8px;
    width: 100%;
  }

  .status {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    gap: 8px;
    align-items: flex-start;
  }

  .refund {
    display: flex;
    flex-flow: row wrap;
    gap: 16px 8px;
    justify-content: space-between;
  }

  .refund > h3 {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .refund > span {
    color: var(--color-main-primary-500);
  }
</style>
