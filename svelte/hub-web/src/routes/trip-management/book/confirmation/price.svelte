<script lang="ts">
  import { formatAmount } from "formatting/currency";
  import { getLocale, getLocaleData } from "i18n";
  import type { Price } from "integration/common/schemas/price";
  import type { TripBooking } from "integration/junction-mobile-api/schemas/booking";

  export let bookings: TripBooking[];

  const locale = getLocale();
  const i18n = getLocaleData();

  $: totalPrice = bookings.reduce<Price>(
    (prev, curr) => ({
      currency: curr.price.total.currency,
      amount: prev.amount + curr.price.total.amount,
    }),
    { amount: 0, currency: "EUR" },
  );
</script>

<div class="price typography body-small">
  <span>{$i18n.sentences.thisPriceIsForAllPassengers}</span>
  <ul>
    <li>
      <span>{$i18n.priceBreakdownTypes["base-fare"]} + {$i18n.priceBreakdownTypes.tax}</span>
      <strong class="typography bold">
        {formatAmount(totalPrice, { locale: $locale, sign: true })}
      </strong>
    </li>

    <li class="typography body-xlarge bold">
      <span>{$i18n.sentences.totalPaid}</span>
      <strong>
        {formatAmount(totalPrice, { locale: $locale, sign: true })}
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
