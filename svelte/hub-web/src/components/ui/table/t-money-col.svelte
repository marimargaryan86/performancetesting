<script lang="ts">
  /* global Typography */
  import TCol from "./t-col.svelte";
  import { formatAmount } from "formatting/currency";
  import { getLocale } from "i18n";
  import type { Price } from "integration/common/schemas/price";

  let className: string | undefined = undefined;
  export { className as class };
  export let currencySize: "small" | "x-small" = "small";
  export let money: Price;
  export let typography: Typography | undefined = undefined;

  const locale = getLocale();
</script>

<TCol class={className} {typography}>
  <div class="money">
    <span>{formatAmount(money, { locale: $locale })}</span>
    <strong typography={currencySize === "small" ? "body-small" : "body-xsmall"}>
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
