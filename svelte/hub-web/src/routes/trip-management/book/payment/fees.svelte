<script lang="ts">
  import { dev } from "$app/environment";
  import { formatAmount } from "formatting/currency";
  import { slideFade } from "transitions/slide-fade";
  import Collapsible from "../../components/collapsible.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";

  const mockedTotalFees = { currency: "EUR", amount: 100 };
  const mockedFeesBreakdown = [
    { type: "Service fee", fee: { currency: "EUR", amount: 75 } },
    { type: "Agency Mark-up", fee: { currency: "EUR", amount: 25 } },
  ];

  let collapsible: Collapsible | undefined;

  $: feesBreakdown = mockedFeesBreakdown;
  $: totalFees = mockedTotalFees;
</script>

{#if !dev}
  <div />
{:else}
  <Collapsible bind:this={collapsible} title="Fees">
    <div class="details">
      {#if feesBreakdown}
        {#each feesBreakdown as item}
          <div class="input-wrapper">
            <TextField
              bind:value={item.fee.amount}
              type="number"
              placeholder="Enter amount"
              label={item.type}
            />

            <SelectField
              options={["EUR", "USD"]}
              bind:value={item.fee.currency}
              placeholder="Select currency"
              label="&nbsp;"
            />
          </div>
        {/each}
      {/if}
    </div>

    <div class="fees" slot="content-after" let:expanded let:transitionTimeMs>
      {#if expanded}
        <div transition:slideFade={{ duration: transitionTimeMs }} class="fees-breakdown">
          {#if feesBreakdown}
            <ul>
              {#each feesBreakdown as item}
                <li>
                  <span class="typography label-medium">{item.type}</span>
                  <span class="typography body-small bold">
                    {formatAmount(item.fee, undefined, true)}
                  </span>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/if}

      <div class="total">
        <span class="typography body-large bold">Total to collect</span>
        <em class="typography body-large bold">
          {#if totalFees}
            {formatAmount(totalFees, undefined, true)}
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
