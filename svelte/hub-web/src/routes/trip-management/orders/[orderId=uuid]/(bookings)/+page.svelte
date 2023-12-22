<script lang="ts">
  import Button from "components/ui/button.svelte";
  import Header from "components/ui/table/header.svelte";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TMoneyCol from "components/ui/table/t-money-col.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import routeConfig from "routeConfig";
  import { getOrigin, getDestination } from "utils/booking";
  import CancellationDialog from "./cancellation-dialog.svelte";
  import TStatusBadgeCol from "components/ui/table/t-status-badge-col.svelte";
  import { getPageTitle } from "utils/page-title";
  import { getLocale, getLocaleData } from "i18n";

  export let data;

  const locale = getLocale();
  const i18n = getLocaleData();

  let cancellationDialog: CancellationDialog | undefined;

  $: showCancellationColumn = data.order.bookings.find((item) => item.cancellationId);
  $: showRefundColumn = data.order.bookings.find((item) => item.refundId);
  $: showActionsColumn = data.order.bookings.find(
    (item) => item.status === "confirmed" && !item.cancellationId,
  );

  function cancelBooking(booking: TripBooking): void {
    cancellationDialog?.open(booking);
  }

  function updateOrders(): void {
    data.order = data.order;
  }

  const orderLink = routeConfig.routes.tripManagement.routes.orders.routes.order(data.order.id);
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.orders.title,
      data.order.journey?.reference ?? $i18n.words.unknown,
      $i18n.pages.tripManagement.pages.orders.pages.bookings.title,
    )}
  </title>
</svelte:head>

<CancellationDialog
  bind:this={cancellationDialog}
  passengers={data.order.passengers}
  on:success={updateOrders}
/>

<Table class="bookings-table">
  <THead>
    <Header>{$i18n.tableHeaders.booking} Booking</Header>
    <Header />
    <Header>{$i18n.tableHeaders.ticket}</Header>
    <Header>{$i18n.tableHeaders.departureDate}</Header>
    <Header>{$i18n.tableHeaders.origin}</Header>
    <Header>{$i18n.tableHeaders.destination}</Header>
    <Header>{$i18n.tableHeaders.totalPrice}</Header>
    <Header>{$i18n.tableHeaders.bookingStatus}</Header>
    {#if showCancellationColumn}<Header>{$i18n.tableHeaders.cancellationStatus}</Header>{/if}
    {#if showRefundColumn}<Header>{$i18n.tableHeaders.refundStatus}</Header>{/if}
    {#if showActionsColumn}<Header />{/if}
  </THead>

  <TBody>
    {#each data.order.bookings as booking, idx}
      {@const origin = getOrigin(booking)}
      {@const destination = getDestination(booking)}

      <TRow>
        <TCol width="0">{idx + 1}</TCol>
        <TCol width="0">
          <a
            href={routeConfig.routes.tripManagement.routes.orders.routes
              .order(data.order.id)
              .routes.booking(booking.id).root}
          >
            {$i18n.actions.view}
          </a>
        </TCol>

        <TCol width="0">
          {#if booking.ticketUrls.length}
            <a
              class="typography body-medium"
              href={orderLink.routes.booking(booking.id).routes.tickets.root}
              download
            >
              {$i18n.actions.download}
            </a>
          {:else}
            <span class="not-available">{$i18n.words.notAvailable}</span>
          {/if}
        </TCol>

        <TCol>
          {booking.detailsList[0]?.legs[0]?.departureAt.toLocaleDateString($locale, {
            timeZone: origin?.timeZone,
          })}
        </TCol>

        <TCol class="typography bold">{origin?.name ?? $i18n.words.unknown}</TCol>
        <TCol class="typography bold">{destination?.name ?? $i18n.words.unknown}</TCol>
        <TMoneyCol money={booking.price.total} />
        <TStatusBadgeCol value={booking.status} />

        {#if showCancellationColumn}
          {#if booking.cancellation?.status}
            <TStatusBadgeCol value={booking.cancellation.status} />
          {:else}
            <TCol width="0" />
          {/if}
        {/if}

        {#if showRefundColumn}
          {#if booking.refund?.status}
            <TStatusBadgeCol value={booking.refund.status} />
          {:else}
            <TCol width="0" />
          {/if}
        {/if}

        {#if showActionsColumn}
          <TActionsCol static>
            {#if booking.status === "confirmed" && !booking.cancellation?.status}
              <Button
                size="xx-small"
                variant="outline"
                on:click={cancelBooking.bind(cancelBooking, booking)}
              >
                {$i18n.actions.cancelRequest}
              </Button>
            {/if}
          </TActionsCol>
        {/if}
      </TRow>
    {/each}
  </TBody>
</Table>

<style>
  :global(.table.bookings-table) {
    width: 100%;
    height: 100%;
  }

  a {
    padding: 0;
    color: var(--color-common-light-text-link);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .not-available {
    color: var(--color-common-light-soft);
  }
</style>
