<script lang="ts">
  import { formatAmount } from "formatting/currency";
  import type { Price } from "integration/common/schemas/price";
  import type { TripBooking } from "integration/junction-mobile-api/schemas/booking";

  export let bookings: TripBooking[];

  $: totalPrice = bookings.reduce<Price>(
    (prev, curr) => ({
      currency: curr.price.total.currency,
      amount: prev.amount + curr.price.total.amount,
    }),
    { amount: 0, currency: "EUR" },
  );
</script>

<div class="price typography body-small">
  <span>The price is for all passengers</span>
  <ul>
    <li>
      <span>Base fare + taxes</span>
      <strong class="typography bold">
        {formatAmount(totalPrice, undefined, true)}
      </strong>
    </li>

    <li class="typography body-xlarge bold">
      <span>Total paid</span>
      <strong>
        {formatAmount(totalPrice, undefined, true)}
      </strong>
    </li>
  </ul>
</div>

<style>
  .price {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 4px;
  }

  li {
    display: flex;
    justify-content: space-between;
  }

  li:last-child {
    margin-top: 12px;
  }

  li:last-child > strong {
    color: var(--color-main-primary-500);
  }
</style>
