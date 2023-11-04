<script lang="ts">
  import TCol from "./t-col.svelte";
  import { formatAmount } from "formatting/currency";
  import type { Price } from "integration/common/schemas/price";
  import type { Currency } from "integration/junction-hub-api/schemas/currency";

  export let money: Price;
  export let currencies: Map<string, Currency> | undefined = undefined;
</script>

<TCol>
  <div class="money">
    <span>{formatAmount(money, currencies)}</span>
    <strong class="typography body-small">{money.currency}</strong>
  </div>
</TCol>

<style>
  .money {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .money > strong {
    color: var(--color-main-neutral-600);
  }
</style>
