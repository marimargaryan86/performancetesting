<script lang="ts">
  import TCol from "./t-col.svelte";
  import { formatAmount } from "formatting/currency";
  import type { Price } from "integration/common/schemas/price";

  let className: string | undefined = undefined;
  export { className as class };
  export let currencySize: "small" | "x-small" = "small";
  export let money: Price;
</script>

<TCol class={className}>
  <div class="money">
    <span>{formatAmount(money)}</span>
    <strong
      class="typography body-small"
      class:body-small={currencySize === "small"}
      class:body-xsmall={currencySize === "x-small"}
    >
      {money.currency}
    </strong>
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
