<script lang="ts">
  import type { Order } from "~/integration/junction-mobile-api/schemas/order";
  import { getOrderStatus } from "~/integration/common/schemas/order";
  import Ticket from "$lib/components/pages/trip-management/booking-flow-train/ticket.svelte";
  import StatusBadge from "$lib/components/ui/status-badge.svelte";
  import { getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";

  export let order: Order;

  const t = getTranslator();
</script>

<div class="overview">
  <h2 typography="headline-small" weight="bold">{$t("sentences.yourOrderHasBeenCreated")}</h2>
  <Ticket identifier={order.journey?.reference} />

  <div class="item">
    <span class="circle target">
      <Icon variant="checked" size="16px" color="var(--color-common-dark-strong)" />
    </span>
    <div>
      <span typography="body-xsmall">{$t("words.status")}</span>
      <StatusBadge value={getOrderStatus.booking(order) ?? "unknown"} />
    </div>
  </div>
</div>

<style>
  .overview {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 26px;
  }

  h2 {
    grid-column: 1 / -1;
  }

  .item {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .item > div {
    display: flex;
    flex-flow: column;
  }

  .item > div > span[typography="body-xsmall"] {
    color: var(--color-main-primary-700);
  }

  .circle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: var(--color-main-primary-600) 1px solid;
    border-radius: 50%;
  }

  .circle.target {
    background-color: var(--color-main-primary-600);
    box-shadow: 0 0 0 8px #ffffff inset;
  }
</style>
