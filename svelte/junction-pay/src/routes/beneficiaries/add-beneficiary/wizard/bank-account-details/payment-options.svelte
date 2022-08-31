<script lang="ts">
  import Checkbox from "$lib/components/checkbox.svelte";
  import type {
    PaymentOption,
    PaymentOptionsData,
    PaymentOptionsError,
  } from "$models/beneficiary-models/models";
  import PatternedTextField from "$lib/components/patterned-text-field.svelte";
  import TextField from "$lib/components/text-field.svelte";

  export let data: Partial<PaymentOptionsData>;
  export let errors: PaymentOptionsError | undefined = undefined;

  const paymentOptions: Record<string, PaymentOption> = {
    "BIC/Swift": "swift",
    "Sort code": "sort-code",
  };
</script>

<ul class="payment-options">
  {#each Object.entries(paymentOptions) as [label, option]}
    <li>
      <Checkbox value={option} bind:group={data.paymentOptions} id="payment-option-{option}" />
      <label for="payment-option-{option}">{label}</label>
    </li>
  {/each}

  {#if errors?.paymentOptions}
    <li class="error">{errors?.paymentOptions.join(", ")}</li>
  {/if}
</ul>

{#if data.paymentOptions?.includes("sort-code")}
  <div class="field">
    <label for="sort-code" class:error={!!errors?.sortCode}>Sort code</label>
    <PatternedTextField
      id="sort-code"
      pattern="99-99-99"
      bind:value={data.sortCode}
      error={errors?.sortCode?.join(" ")}
    />
  </div>
{/if}

{#if data.paymentOptions?.includes("swift")}
  <div class="field">
    <label for="bic-swift" class:error={!!errors?.bicSwift}>BIC/SWIFT</label>
    <TextField
      id="bic-swift"
      bind:value={data.bicSwift}
      placeholder="Enter BIC/SWIFT"
      error={errors?.bicSwift?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="iban" class:error={!!errors?.iban}>IBAN</label>
    <TextField
      id="iban"
      bind:value={data.iban}
      placeholder="Enter IBAN"
      error={errors?.iban?.join(", ")}
    />
  </div>
{/if}

<style>
  .payment-options {
    grid-column: 1 / -1;
    margin: 0 0 0 8px;
  }

  .field > label {
    display: block;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  li {
    display: inline-block;
    margin: 0 32px 0 -8px;
  }

  li > :global(.checkbox) {
    margin-right: 8px;
    vertical-align: middle;
  }

  .field > :global(.text-field) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    padding: 0 18px;
    width: 100%;
  }

  .error {
    color: var(--color-red);
  }

  li.error {
    display: block;
    font-size: 14px;
    margin: 4px 0;
  }
</style>
