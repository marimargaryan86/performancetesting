<script lang="ts">
  import { getPageTitle } from "$lib/utils/page-title";
  import Passengers from "$lib/components/pages/trip-management/booking-flow-train/passengers.svelte";
  import Ticket from "$lib/components/pages/trip-management/booking-flow-train/ticket.svelte";
  import { getTranslator } from "$lib/i18n";

  export let data;

  const t = getTranslator();
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.orders.title"),
      data.order.journey?.reference ?? $t("words.unknown"),
      $t("pages.tripManagement.pages.orders.pages.details.title"),
    )}
  </title>
</svelte:head>

<div class="content">
  <h3 typography="title-large" weight="bold">{$t("words.orderDetails")}</h3>

  <Ticket identifier={data.order.journey?.reference} />

  <Passengers passengers={data.order.passengers} />
</div>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 24px;
    max-width: 1152px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h3 {
    color: var(--color-main-neutral-800);
  }

  .content > :global(.passengers) {
    margin-top: 24px;
  }
</style>
