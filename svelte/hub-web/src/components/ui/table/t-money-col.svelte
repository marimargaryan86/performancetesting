<script lang="ts">
  import TCol from "./t-col.svelte";
  import { formatAmount } from "formatting/currency";
  import type { PriceModel } from "integration/junction-mobile-api/schemas/price";
  import type { CurrencyModel } from "integration/junction-pay/schemas/money";

  export let money: PriceModel;
  export let currencies: Map<string, CurrencyModel> | undefined = undefined;
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
