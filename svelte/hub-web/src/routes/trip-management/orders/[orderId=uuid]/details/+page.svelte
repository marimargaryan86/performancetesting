<script lang="ts">
  import { getPageTitle } from "~/utils/page-title";
  import Passengers from "../../../components/passengers.svelte";
  import Ticket from "../../../components/ticket.svelte";
  import { getLocaleData } from "~/i18n";

  export let data;

  const i18n = getLocaleData();
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.tripManagement.title,
      $i18n.pages.tripManagement.pages.orders.title,
      data.order.journey?.reference ?? $i18n.words.unknown,
      $i18n.pages.tripManagement.pages.orders.pages.details.title,
    )}
  </title>
</svelte:head>

<div class="content">
  <h3 typography="title-large" weight="bold">{$i18n.words.orderDetails}</h3>

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
