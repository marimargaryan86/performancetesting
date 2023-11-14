<script lang="ts">
  import StatusBadge from "components/ui/status-badge.svelte";
  import { formatAmount } from "formatting/currency";
  import type { Refund } from "integration/junction-hub-api/schemas/refund";
  import { slideFade } from "transitions/slide-fade";

  export let refund: Refund;
</script>

<div class="refund" transition:slideFade={{ duration: 300 }}>
  <h3 class="typography title-large bold">
    Refund

    <StatusBadge value={refund.status} />
  </h3>

  <ul class="money">
    {#if refund.refunded.us}
      <li class="typography body-medium amount">
        <strong>To us</strong>
        <span class="typography bold" class:negative={refund.refunded.us.amount < 0}>
          {formatAmount(refund.refunded.us, true)}
        </span>
      </li>
    {/if}

    {#if refund.refunded.usInPayerCurrency}
      <li class="typography body-medium amount">
        <strong>To us <em>(Payer currency)</em></strong>
        <span class="typography bold" class:negative={refund.refunded.usInPayerCurrency.amount < 0}>
          {refund.refunded.usInPayerCurrency
            ? formatAmount(refund.refunded.usInPayerCurrency, true)
            : "N/A"}
        </span>
      </li>
    {/if}

    {#if refund.refunded.reseller}
      <li class="typography body-medium amount">
        <strong>To reseller</strong>
        <span class="typography bold" class:negative={refund.refunded.reseller.amount < 0}>
          {formatAmount(refund.refunded.reseller, true)}
        </span>
      </li>
    {/if}

    {#if refund.refundPosition}
      <li class="typography body-medium amount">
        <strong>Refund position</strong>
        <span class="typography bold" class:negative={refund.refundPosition.amount < 0}>
          {formatAmount(refund.refundPosition, true)}
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
