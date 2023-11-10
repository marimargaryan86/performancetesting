<script lang="ts">
  import StatusBadge from "components/ui/status-badge.svelte";
  import currencyData from "data/currencyData";
  import { formatAmount } from "formatting/currency";
  import type { Refund } from "integration/junction-hub-api/schemas/refund";
  import { slideFade } from "transitions/slide-fade";

  export let refund: Refund;
</script>

<div class="refund" transition:slideFade={{ duration: 300 }}>
  <h3 class="typography body-large bold">
    Refund

    <StatusBadge value={refund.status} />
  </h3>

  <div class="typography body-xlarge bold amount">
    <strong>Total refunded</strong>
    <span>{formatAmount(refund.refunded.reseller, currencyData.mapping, true)}</span>
  </div>
</div>

<style>
  .refund {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  h3 {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .amount {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .amount > span {
    color: var(--color-main-primary-500);
  }
</style>
