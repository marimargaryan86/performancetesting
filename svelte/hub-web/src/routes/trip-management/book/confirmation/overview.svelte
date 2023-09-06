<script lang="ts">
  import CheckedIcon from "components/icons/checked-icon.svelte";
  import TicketIcon from "components/icons/ticket-icon.svelte";
  import type { OrderModel } from "integration/junction-mobile-api/schemas/order";

  export let order: OrderModel;
</script>

<div class="overview">
  <h2 class="typography headline-small bold">Your order has been confirmed</h2>
  <div class="item">
    <span class="circle">
      <TicketIcon color="var(--color-main-primary-600)" />
    </span>
    <div>
      <span class="typography body-xsmall"> Order reference </span>
      <strong class="typography body-medium bold">
        {order.journey?.reference ?? "-"}
      </strong>
    </div>
  </div>
  <div class="item">
    <span class="circle target">
      <CheckedIcon color="var(--color-common-dark-strong)" />
    </span>
    <div>
      <span class="typography body-xsmall">Status</span>
      <strong class="typography body-medium bold">Confirmed</strong>
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

  .item > div > .body-xsmall {
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
