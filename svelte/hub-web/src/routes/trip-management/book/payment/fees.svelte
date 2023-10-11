<script lang="ts" context="module">
  const feeTypes = ["flat-rate", "percentage"] as const;
  const feeType = z.enum(feeTypes);
  type FeeType = z.infer<typeof feeType>;

  const FALLBACK_CURRENCY = "EUR";

  function roundCurrency(num: number): number {
    return Math.round((num + Number.EPSILON) * 100) / 100;
  }
</script>

<script lang="ts">
  import { z } from "zod";
  import { dev } from "$app/environment";
  import { slideFade } from "transitions/slide-fade";
  import Collapsible from "../../components/collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatAmount } from "formatting/currency";
  import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";

  export let priceQuote: TripOfferPriceQuoteModel | undefined = undefined;
  export let orderMarkup;
  let collapsible: Collapsible | undefined;
  let serviceFeeType: FeeType;
  let agencyMarkupType: FeeType;

  function formatFeeType(option?: FeeType): string {
    return option
      ? {
          "flat-rate": currency,
          percentage: "%",
        }[option]
      : "";
  }

  function calcFeeAmount(type: FeeType, amount: number, totalPriceAmount: number): number {
    switch (type) {
      case "flat-rate":
        return roundCurrency(amount);

      case "percentage":
        return roundCurrency((amount / 100) * totalPriceAmount);

      default:
        return NaN;
    }
  }

  $: totalPrice = priceQuote?.price ?? { currency, amount: 0 };
  $: currency = priceQuote?.price?.currency ?? FALLBACK_CURRENCY;
  $: serviceFeeType = feeType.Enum["flat-rate"];
  $: serviceFeeAmount = 0;
  $: agencyMarkupType = feeType.Enum["flat-rate"];
  $: agencyMarkupAmount = 0;
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
  $: totalToCollectAmount =
    totalPrice.amount + calculatedServiceFeeAmount + calculatedAgencyMarkupAmount;
  $: orderMarkup = {};
</script>

{#if !dev}
  <div />
{:else}
  <Collapsible bind:this={collapsible} title="Fees">
    <div class="details">
      <div class="input-wrapper">
        <TextField
          bind:value={serviceFeeAmount}
          type="number"
          min="0"
          step="0.01"
          placeholder="Enter amount"
          label="Service fee"
        />

        <SelectField
          formatter={formatFeeType}
          options={feeTypes}
          bind:value={serviceFeeType}
          placeholder="Select fee type"
          label="&nbsp;"
        />

        <TextField
          bind:value={agencyMarkupAmount}
          type="number"
          min="0"
          step="0.01"
          placeholder="Enter amount"
          label="Agency mark-up"
        />

        <SelectField
          formatter={formatFeeType}
          options={feeTypes}
          bind:value={agencyMarkupType}
          placeholder="Select fee type"
          label="&nbsp;"
        />
      </div>
    </div>

    <div class="fees" slot="content-after" let:expanded let:transitionTimeMs>
      {#if expanded}
        <div transition:slideFade={{ duration: transitionTimeMs }} class="fees-breakdown">
          <ul>
            <li>
              <span class="typography label-medium">Service fee</span>
              <span class="typography body-small bold">
                {formatAmount({ currency, amount: calculatedServiceFeeAmount }, undefined, true)}
              </span>
            </li>
            <li>
              <span class="typography label-medium">Agency mark-up</span>
              <span class="typography body-small bold">
                {formatAmount({ currency, amount: calculatedAgencyMarkupAmount }, undefined, true)}
              </span>
            </li>
          </ul>
        </div>
      {/if}

      <div class="total">
        <span class="typography body-large bold">Total to collect</span>
        <em class="typography body-large bold">
          {#if priceQuote?.price}
            {formatAmount({ currency, amount: totalToCollectAmount }, undefined, true)}
          {:else}
            <LoadingIcon size="16px" />
          {/if}
        </em>
      </div>
    </div>
  </Collapsible>
{/if}

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
