<script lang="ts">
  import type { TripBooking } from "~/integration/junction-hub-api/schemas/booking";
  import routeConfig from "~/route-config";
  import { getOrigin, getDestination } from "~/utils/booking";
  import CancellationDialog from "./cancellation-dialog.svelte";
  import { getPageTitle } from "~/utils/page-title";
  import { getLocale, getTranslator } from "~/i18n";
  import { ensureDefined } from "~/utils/array";
  import StatusBadge from "~/components/ui/status-badge.svelte";
  import { formatAmount } from "~/formatting/currency";

  export let data;

  const locale = getLocale();
  const t = getTranslator();

  let cancellationDialog: CancellationDialog | undefined;

  $: showCancellationColumn = data.order.bookings.find((item) => item.cancellationId);
  $: showRefundColumn = data.order.bookings.find((item) => item.refundId);
  $: showActionsColumn = data.order.bookings.find(
    (item) => item.status === "confirmed" && !item.cancellationId,
  );
  $: statusColumns = [showCancellationColumn, showRefundColumn, showActionsColumn].filter(
    ensureDefined,
  ).length;
  $: columns = `repeat(3, min-content) repeat(5, 1fr)${
    statusColumns > 0 ? ` repeat(${statusColumns}, min-content)` : ""
  }`;

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
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.orders.title"),
      data.order.journey?.reference ?? $t("words.unknown"),
      $t("pages.tripManagement.pages.orders.pages.bookings.title"),
    )}
  </title>
</svelte:head>

<CancellationDialog
  bind:this={cancellationDialog}
  passengers={data.order.passengers}
  on:success={updateOrders}
/>

<x-table class="bookings-table" style:grid-template-columns={columns}>
  <x-thead>
    <x-th>{$t("tableHeaders.booking")}</x-th>
    <x-th />
    <x-th>{$t("tableHeaders.ticket")}</x-th>
    <x-th>{$t("tableHeaders.departureDate")}</x-th>
    <x-th>{$t("tableHeaders.origin")}</x-th>
    <x-th>{$t("tableHeaders.destination")}</x-th>
    <x-th>{$t("tableHeaders.totalPrice")}</x-th>
    <x-th>{$t("tableHeaders.bookingStatus")}</x-th>
    {#if showCancellationColumn}<x-th>{$t("tableHeaders.cancellationStatus")}</x-th>{/if}
    {#if showRefundColumn}<x-th>{$t("tableHeaders.refundStatus")}</x-th>{/if}
    {#if showActionsColumn}<x-th />{/if}
  </x-thead>

  {#each data.order.bookings as booking, idx}
    {@const origin = getOrigin(booking)}
    {@const destination = getDestination(booking)}

    <x-tr>
      <x-td width="0">{idx + 1}</x-td>
      <x-td width="0">
        <a
          href={routeConfig.routes.tripManagement.routes.orders.routes
            .order(data.order.id)
            .routes.booking(booking.id).root}
        >
          {$t("actions.view")}
        </a>
      </x-td>

      <x-td width="0">
        {#if booking.ticketUrls.length}
          <a
            typography="body-medium"
            href={orderLink.routes.booking(booking.id).routes.tickets.root}
            download
          >
            {$t("actions.download")}
          </a>
        {:else}
          <span class="not-available">{$t("words.notAvailable")}</span>
        {/if}
      </x-td>

      <x-td>
        {booking.detailsList[0]?.legs[0]?.departureAt.toLocaleDateString($locale, {
          timeZone: origin?.timeZone,
        })}
      </x-td>

      <x-td weight="bold">{origin?.name ?? $t("words.unknown")}</x-td>
      <x-td weight="bold">{destination?.name ?? $t("words.unknown")}</x-td>
      <x-td>{formatAmount(booking.price.total, { locale: $locale, sign: true })}</x-td>
      <x-td><StatusBadge value={booking.status} /></x-td>

      {#if showCancellationColumn}
        <x-td>
          {#if booking.cancellation?.status}
            <StatusBadge value={booking.cancellation.status} />
          {/if}
        </x-td>
      {/if}

      {#if showRefundColumn}
        <x-td>
          {#if booking.refund?.status}
            <StatusBadge value={booking.refund.status} />
          {/if}
        </x-td>
      {/if}

      {#if showActionsColumn}
        <x-tactions>
          {#if booking.status === "confirmed" && !booking.cancellation?.status}
            <button
              size="xx-small"
              variant="outline"
              on:click={cancelBooking.bind(cancelBooking, booking)}
            >
              {$t("actions.cancelRequest")}
            </button>
          {/if}
        </x-tactions>
      {/if}
    </x-tr>
  {/each}
</x-table>

<style>
  .bookings-table {
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
