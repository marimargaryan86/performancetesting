<script lang="ts">
  import { formatAmountAndCode } from "formatting/currency";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";

  export let booking: TripBooking;
</script>

<div class="billing">
  <h3 class="typography title-medium bold">Billing</h3>

  <div class="table">
    <span class="typography body-small bold">Description</span>
    <span class="typography body-small bold right-align">Price</span>

    <span class="typography body-small subtle">Fare</span>
    <span class="typography body-small bold right-align">
      {formatAmountAndCode(booking.price.total)}
    </span>

    <hr />

    <span class="typography body-large subtle">Total</span>
    <span class="typography body-large bold right-align">
      {formatAmountAndCode(booking.price.total)}
    </span>
  </div>
</div>

<style>
  .billing {
    padding: 24px;
    color: var(--color-main-neutral-800);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  h3 {
    grid-column: 1 / -1;
    margin-bottom: 24px;
  }

  .table {
    display: grid;
    grid-template-columns: 1fr max-content;
    gap: 16px;
  }

  hr {
    grid-column: 1 / -1;
    margin: 0;
    border: 0;
    border-bottom: var(--color-main-neutral-400) 1px solid;
  }

  .right-align {
    text-align: right;
  }

  .subtle {
    color: var(--color-main-neutral-500);
  }
</style>
