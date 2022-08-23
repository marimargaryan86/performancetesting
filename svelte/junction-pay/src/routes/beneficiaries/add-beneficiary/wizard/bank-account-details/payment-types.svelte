<script lang="ts">
  import countriesData from "$content/countries";
  import Checkbox from "$lib/components/checkbox.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { PaymentTypeData, PaymentTypeError } from "$models/beneficiary-models/models";

  export let data: Partial<PaymentTypeData>;
  export let errors: PaymentTypeError | undefined = undefined;

  const countries = countriesData;
</script>

<ul class="payment-types">
  <li>
    <Checkbox value="priority" bind:group={data.paymentTypes} id="payment-type-priority" />
    <label for="payment-type-priority">Priority</label>
  </li>

  <li>
    <Checkbox value="regular" bind:group={data.paymentTypes} id="payment-type-regular" />
    <label for="payment-type-regular">Regular</label>
  </li>

  {#if errors?.paymentTypes}
    <li class="error">{errors?.paymentTypes.join(", ")}</li>
  {/if}
</ul>

<div class="field">
  <label for="beneficiary-account-country" class:error={!!errors?.addressCountry}>
    Beneficiary country
  </label>
  <SelectField
    items={countries}
    disabled
    displayValue={(value) => value?.name ?? ""}
    value={data.addressCountry}
    id="beneficiary-account-currency"
    placeholder="Select country"
    error={errors?.addressCountry?.join(", ")}
  />
</div>

<div class="field">
  <label for="address-line" class:error={!!errors?.addressLine}>Beneficiary address</label>
  <TextField
    id="address-line"
    bind:value={data.addressLine}
    placeholder="Enter beneficiary address"
    error={errors?.addressLine?.join(", ")}
  />
</div>

<div class="field">
  <label for="postal-code" class:error={!!errors?.addressPostalCode}>
    Beneficiary postal code
  </label>
  <TextField
    id="postal-code"
    bind:value={data.addressPostalCode}
    placeholder="Enter postal code"
    error={errors?.addressPostalCode?.join(", ")}
  />
</div>

<style>
  .payment-types {
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
    padding: 0 18px;
  }

  .field > :global(.text-field),
  .field > :global(.select-field.select-field) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
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
