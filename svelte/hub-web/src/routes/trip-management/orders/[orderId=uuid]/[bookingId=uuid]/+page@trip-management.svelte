<script lang="ts">
  import type { BreadCrumb } from "$lib/models/ui";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import routeConfig from "$lib/route-config";
  import { getDestination, getOrigin } from "$lib/utils/booking";
  import Passengers from "$lib/components/pages/trip-management/book/passengers.svelte";
  import Ticket from "$lib/components/pages/trip-management/book/ticket.svelte";
  import Itinerary from "$lib/components/pages/trip-management/book/itinerary.svelte";
  import StatusBadge from "$lib/components/ui/status-badge.svelte";
  import { getUser, permitted } from "$lib/utils/permissions";
  import Admin from "$lib/components/pages/trip-management/orders/admin.svelte";
  import { formatAmount } from "$lib/formatting/currency";
  import Fees from "$lib/components/pages/trip-management/book/confirmation/rail-components/fees.svelte";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getLocale, getTranslator } from "$lib/i18n";
  import Price from "$lib/components/pages/trip-management/book/price.svelte";

  export let data;

  const locale = getLocale();
  const t = getTranslator();
  const user = getUser();

  let breadCrumbs: BreadCrumb[];

  $: i18nOrders = $t("pages.tripManagement.pages.orders", { returnObjects: true });
  $: order = data.booking.order;
  $: reservationNo = data.booking.operatorBookingReferences.length
    ? data.booking.operatorBookingReferences.join(", ")
    : undefined;
  $: bookingTitle = `${$t("words.booking")} ${data.bookingNo}`;
  $: orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.booking.orderId);
  $: selfLink = orderLink.routes.booking(data.booking.id);
  $: breadCrumbs = [
    { label: i18nOrders.title, url: routeConfig.routes.tripManagement.routes.orders.root },
    { label: order?.journey?.reference ?? $t("words.unknown"), url: orderLink.root },
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
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.orders.title"),
      order?.journey?.reference ?? "Unknown",
      bookingTitle,
    )}
  </title>
</svelte:head>

<StandardLayout {breadCrumbs}>
  <svelte:fragment slot="page-title">
    {bookingTitle}:
    <span typography="title-large" weight="bold">
      {getOrigin(data.booking)?.name ?? $t("words.unknown")}
      {$t("words.to").toLowerCase()}
      {getDestination(data.booking)?.name ?? $t("words.unknown")}
    </span>
  </svelte:fragment>

  <div class="content" style:--grid-columns={canViewTransactions ? "1fr 1fr" : "1fr"}>
    <div class="booking">
      <div class="itinerary">
        <h3 typography="title-large" weight="bold">{$t("words.itinerary")}</h3>

        <Ticket identifier={reservationNo} title={$t("words.reservationNumber")} />

        {#if order}
          <Price bookings={order.bookings} />
        {/if}

        {#if data.markups}
          <Fees markups={data.markups} />
        {/if}

        <div class="statuses">
          <div class="status" typography="body-small" weight="bold">
            {$t("words.bookingStatus")}
            <StatusBadge value={data.booking.status} />
          </div>

          {#if data.booking.cancellation?.status}
            <div class="status" typography="body-small" weight="bold">
              {$t("words.cancellationStatus")}
              <StatusBadge value={data.booking.cancellation.status} />
            </div>
          {/if}
        </div>
      </div>

      {#if data.booking.refund}
        <div class="refund" typography="body-medium" weight="bold">
          <h3 typography="body-large" weight="bold">
            {$t("words.refund")}

            <StatusBadge value={data.booking.refund.status} />
          </h3>
          <strong>{$t("words.total")}</strong>
          <span>
            {data.booking.refund.refunded.reseller
              ? formatAmount(data.booking.refund.refunded.reseller, $locale, { sign: true })
              : $t("words.notAvailable")}
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
