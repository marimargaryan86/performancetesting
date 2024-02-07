<script lang="ts">
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "~/i18n";
  import type { Price } from "~/integration/common/schemas/price";
  import type { TripBooking as MobileTripBooking } from "~/integration/junction-mobile-api/schemas/booking";
  import type { TripBooking as HubTripBooking } from "~/integration/junction-hub-api/schemas/booking";

  export let bookings: MobileTripBooking[] | HubTripBooking[];

  const locale = getLocale();
  const t = getTranslator();

  $: totalPrice = bookings.reduce<Price>(
    (prev, curr) => ({
      currency: curr.price.total.currency,
      amount: prev.amount + curr.price.total.amount,
    }),
    { amount: 0, currency: "EUR" },
  );
</script>

<div class="price" typography="body-small">
  <span>{$t("sentences.thisPriceIsForAllPassengers")}</span>
  <ul>
    <li>
      <span>{$t(`priceBreakdownTypes.base-fare`)} + {$t("priceBreakdownTypes.tax")}</span>
      <strong weight="bold">
        {formatAmount(totalPrice, $locale, { sign: true })}
      </strong>
    </li>

    <li typography="body-xlarge" weight="bold">
      <span>{$t("sentences.totalPaid")}</span>
      <strong>
        {formatAmount(totalPrice, $locale, { sign: true })}
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
