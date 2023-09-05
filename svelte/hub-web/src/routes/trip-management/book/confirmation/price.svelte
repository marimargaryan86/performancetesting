<script lang="ts">
  import { formatAmount } from "formatting/currency";
  import type { Infer } from "integration/junction-mobile-api/schema-model.server";
  import type { priceModel } from "integration/junction-mobile-api/schemas/price";
  import type { bookingModel } from "integration/junction-mobile-api/schemas/booking";

  export let bookings: Infer<typeof bookingModel>[];

  $: totalPrice = bookings.reduce<Infer<typeof priceModel>>(
    (prev, curr) => ({ currency: curr.price.currency, amount: prev.amount + curr.price.amount }),
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
      <span>Total to pay</span>
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
