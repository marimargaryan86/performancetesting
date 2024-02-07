<script lang="ts">
  import { formatAmount } from "$lib/formatting/currency";
  import { getLocale, getTranslator } from "~/i18n";
  import type { Refund } from "~/integration/junction-hub-api/schemas/refund";
  import { slideFade } from "~/transitions/slide-fade";
  import { pricesEqual } from "~/utils/money";

  export let refund: Refund;

  const locale = getLocale();
  const t = getTranslator();

  // Only display usInPayerCurrency if the currency differs from refundedUs
  $: usInPayerCurrency =
    refund.refunded.usInPayerCurrency &&
    refund.refunded.us &&
    pricesEqual(refund.refunded.us, refund.refunded.usInPayerCurrency)
      ? undefined
      : refund.refunded.usInPayerCurrency;
</script>

<div class="refund" transition:slideFade={{ duration: 300 }}>
  <h3 typography="title-large" weight="bold">{$t("words.refund")}</h3>

  <ul class="money">
    {#if refund.refunded.us}
      <li class="amount" typography="body-medium">
        <strong>{$t("sentences.toUs")}</strong>
        <span weight="bold" class:negative={refund.refunded.us.amount < 0}>
          {formatAmount(refund.refunded.us, $locale, { sign: true })}
        </span>
      </li>
    {/if}

    {#if usInPayerCurrency}
      <li class="amount" typography="body-medium">
        <strong>{$t("sentences.toUs")} <em>({$t("sentences.payerCurrency")})</em></strong>
        <span weight="bold" class:negative={usInPayerCurrency.amount < 0}>
          {formatAmount(usInPayerCurrency, $locale, { sign: true })}
        </span>
      </li>
    {/if}

    {#if refund.refunded.reseller}
      <li class="amount" typography="body-medium">
        <strong>{$t("sentences.toReseller")}</strong>
        <span weight="bold" class:negative={refund.refunded.reseller.amount < 0}>
          {formatAmount(refund.refunded.reseller, $locale, { sign: true })}
        </span>
      </li>
    {/if}

    {#if refund.refundPosition}
      <li class="amount" typography="body-medium">
        <strong>{$t("words.refundPosition")}</strong>
        <span weight="bold" class:negative={refund.refundPosition.amount < 0}>
          {formatAmount(refund.refundPosition, $locale, { sign: true })}
        </span>
      </li>
    {/if}
  </ul>
</div>

<style>
  .refund {
    display: flex;
    flex-flow: column;
    gap: 32px;
    padding: 32px 48px 48px;
    color: var(--color-main-primary-900);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h3 {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .money {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .amount {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .amount > span {
    color: var(--color-main-primary-600);
  }

  .amount > span.negative {
    color: var(--color-semantic-error-600);
  }

  .amount > strong > em {
    color: var(--color-main-neutral-500);
  }
</style>
