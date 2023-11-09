<script lang="ts">
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import { formatAmount, formatPriceBreakdownType } from "formatting/currency";
  import type { Price, PriceBreakdown } from "integration/common/schemas/price";
  import type { Company } from "integration/junction-hub-api/schemas/company";
  import type { Markups } from "integration/junction-mobile-api/schemas/markups";

  export let company: Company | undefined;
  export let title: string;
  export let price: Price;
  export let breakdownList: PriceBreakdown[];
  export let markupsTask: Promise<Markups | undefined> | undefined = undefined;

  async function getTotal(
    nextPrice: Price,
    nextMarkupsTask?: Promise<Markups | undefined>,
  ): Promise<Price> {
    if (!nextMarkupsTask) {
      return nextPrice;
    }

    const markups = await nextMarkupsTask;

    if (markups) {
      return {
        currency: nextPrice.currency,
        amount: markups.agencyMarkup.amount + nextPrice.amount,
      };
    }

    return nextPrice;
  }

  $: totalTask = getTotal(price, markupsTask);
</script>

<div class="company">
  <span class="typography body-medium">{title}</span>

  {#if company}
    <span class="typography body-large bold company-name">
      <EntityAvatar name={company.name} size="24px" />
      {company.name}
    </span>

    <div class="breakdown typography label-medium">
      {#each breakdownList as breakdown}
        <span>{formatPriceBreakdownType(breakdown.type)}</span>
        <strong>
          {formatAmount(breakdown.price)}
          <em class="typography body-xsmall">{breakdown.price.currency}</em>
        </strong>
      {/each}

      {#if markupsTask}
        {#await markupsTask}
          <LoadingIcon size="16px" />
        {:then markups}
          {#if markups}
            <span>Markup</span>
            <strong>
              {formatAmount(markups.agencyMarkup)}
              <em class="typography body-xsmall">{markups.agencyMarkup.currency}</em>
            </strong>
          {/if}
        {/await}
      {/if}

      <span>Total</span>
      {#await totalTask}
        <LoadingIcon size="16px" />
      {:then total}
        <strong>
          {formatAmount(total)} <em class="typography body-xsmall">{total.currency}</em>
        </strong>
      {/await}
    </div>
  {:else}
    <span class="typography body-small bold">N/A</span>
  {/if}
</div>

<style>
  .company {
    display: flex;
    flex-flow: column;
    gap: 4px;
  }

  .company-name {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .breakdown {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
    margin-top: 12px;
  }

  .breakdown strong {
    text-align: right;
  }

  .breakdown em {
    color: var(--color-common-light-soft);
  }
</style>
