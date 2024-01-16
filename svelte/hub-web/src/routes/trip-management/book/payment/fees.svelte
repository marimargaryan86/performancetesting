<script lang="ts" context="module">
  const feeTypes = ["flat-rate", "percentage"] as const;
  export type FeeType = (typeof feeTypes)[number];

  const FALLBACK_CURRENCY = "EUR";

  /**
   * Given the markup fee type, raw input amount, and the baseline total price,
   * this returns the correct fee amount. Applies rounding to percentage-based
   * fees.
   *
   * @param {FeeType} type - Supported values are "flat-rate" or "percentage".
   * @param {number} inputAmount - The amount on which the fee is calculated.
   * @param {number} baselineAmount - When calculating a percentage, this is the baseline amount.
   * @returns {number} - The calculated fee rounded to the nearest hundredth. Returns `NaN` for unsupported fee types.
   *
   * @example
   * calcFeeAmount("flat-rate", 150.42, 0);        // returns 150.42
   * calcFeeAmount("percentage", 2, 1000);         // returns 20
   * calcFeeAmount("unsupported-type", 200, 1000); // returns NaN, should an incorrect type be passed
   */
  export function calcFeeAmount(
    type: FeeType,
    inputAmount: number,
    baselineAmount: number,
  ): number {
    switch (type) {
      case "flat-rate":
        return roundCurrency(inputAmount);

      case "percentage":
        return roundCurrency((inputAmount / 100) * baselineAmount);

      default:
        return NaN;
    }
  }
</script>

<script lang="ts">
  import { roundCurrency } from "utils/money";
  import { slideFade } from "transitions/slide-fade";
  import Collapsible from "../../components/collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatAmount } from "formatting/currency";
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import type { MarkupsCreate } from "integration/junction-mobile-api/schemas/markups";
  import { getLocale, getLocaleData } from "i18n";

  export let priceQuote: TripOfferPriceQuote | undefined = undefined;
  export let orderMarkups: MarkupsCreate;

  const locale = getLocale();
  const i18n = getLocaleData();

  let collapsible: Collapsible | undefined;
  let serviceFeeType: FeeType = feeTypes[0];
  let agencyMarkupType: FeeType = feeTypes[0];
  let serviceFeeAmount = 0;
  let agencyMarkupAmount = 0;

  /**
   * Returns a formatted string for the fee type select field. Must stay in
   * scope in order to access `$currency` and comply with the
   * `SelectField.formatter` property.
   *
   */
  function formatFeeType(option?: FeeType): string {
    return option
      ? {
          "flat-rate": currency,
          percentage: "%",
        }[option]
      : "";
  }

  $: currency = priceQuote?.price.total?.currency ?? FALLBACK_CURRENCY;
  $: totalPrice = priceQuote?.price.total ?? { currency, amount: 0 };
  $: calculatedServiceFeeAmount = calcFeeAmount(
    serviceFeeType,
    serviceFeeAmount,
    totalPrice.amount,
  );
  $: calculatedAgencyMarkupAmount = calcFeeAmount(
    agencyMarkupType,
    agencyMarkupAmount,
    totalPrice.amount,
  );
  $: totalToCollectAmount = roundCurrency(
    totalPrice.amount + calculatedServiceFeeAmount + calculatedAgencyMarkupAmount,
  );
  $: orderMarkups = {
    orderId: "",
    serviceFee: {
      currency,
      amount: calculatedServiceFeeAmount,
    },
    agencyMarkup: {
      currency,
      amount: calculatedAgencyMarkupAmount,
    },
    totalToCollect: {
      currency,
      amount: totalToCollectAmount,
    },
  };
</script>

<Collapsible bind:this={collapsible} title={$i18n.words.fee.plural}>
  <div class="details">
    <div class="input-wrapper">
      <TextField
        bind:value={serviceFeeAmount}
        type="number"
        min="0"
        step="0.01"
        placeholder={$i18n.actions.enterAmount}
        label={$i18n.words.serviceFee}
      />

      <SelectField
        formatter={formatFeeType}
        options={feeTypes}
        bind:value={serviceFeeType}
        placeholder={$i18n.actions.selectFeeType}
        label="&nbsp;"
      />

      <TextField
        bind:value={agencyMarkupAmount}
        type="number"
        min="0"
        step="0.01"
        placeholder={$i18n.actions.enterAmount}
        label={$i18n.words.agencyMarkup}
      />

      <SelectField
        formatter={formatFeeType}
        options={feeTypes}
        bind:value={agencyMarkupType}
        placeholder={$i18n.actions.selectFeeType}
        label="&nbsp;"
      />
    </div>
  </div>

  <div class="fees" slot="content-after" let:expanded let:transitionTimeMs>
    {#if expanded}
      <div transition:slideFade={{ duration: transitionTimeMs }} class="fees-breakdown">
        <ul>
          <li>
            <span typography="label-medium">{$i18n.words.serviceFee}</span>
            <span typography="body-small" weight="bold">
              {formatAmount(
                { currency, amount: calculatedServiceFeeAmount },
                { locale: $locale, sign: true },
              )}
            </span>
          </li>
          <li>
            <span typography="label-medium">{$i18n.words.agencyMarkup}</span>
            <span typography="body-small" weight="bold">
              {formatAmount(
                { currency, amount: calculatedAgencyMarkupAmount },
                { locale: $locale, sign: true },
              )}
            </span>
          </li>
        </ul>
      </div>
    {/if}

    <div class="total">
      <span typography="body-large" weight="bold">{$i18n.sentences.totalToCollect}</span>
      <em typography="body-large" weight="bold">
        {#if priceQuote?.price}
          {formatAmount(
            { currency, amount: totalToCollectAmount },
            { locale: $locale, sign: true },
          )}
        {:else}
          <LoadingIcon size="16px" />
        {/if}
      </em>
    </div>
  </div>
</Collapsible>

<style>
  .details {
    display: flex;
    flex-flow: column;
    gap: 16px;
    padding: 0 0 16px;
    border-bottom: var(--color-common-line-medium) 1px solid;
  }

  .details :global(.select-field),
  .details :global(.text-field) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --height: 40px;
  }

  .input-wrapper {
    display: grid;
    grid-template-columns: 1fr 96px;
    gap: 16px;
  }

  .fees {
    margin: 0 -16px;
    padding: 16px;
    border: 1px solid var(--color-main-neutral-100);
    border-radius: 16px;
  }

  .fees-breakdown {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .fees-breakdown > ul {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 0 0 16px;
  }

  .fees-breakdown > ul > li {
    display: flex;
    justify-content: space-between;
  }

  .total {
    display: flex;
    justify-content: space-between;
  }
</style>
