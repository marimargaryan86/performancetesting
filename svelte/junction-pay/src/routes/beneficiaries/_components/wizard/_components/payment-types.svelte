<script lang="ts">
  import Checkbox from "$lib/components/checkbox.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import { wizardStore } from "$lib/stores";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";
  import AddressForm from "./address-form.svelte";

  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined> = {};
  export let data: Partial<AddBeneficiaryBankDetailsCombined>;
  $: wizard = $wizardStore;
</script>

<div class="radio-container">
  <div class="priority">
    <Checkbox value="priority" bind:group={data.paymentTypes} id="priority" checked={false} />
    <label for="priority">Priority</label>
  </div>
  <div class="regular">
    <Checkbox value="regular" bind:group={data.paymentTypes} id="regular" checked={false} />
    <label for="regular">Regular</label>
  </div>
</div>
{#if data.paymentTypes.length > 0}
  <AddressForm {errors} {data} />
  <div class="field">
    <label for="bank-account-country"> Bank account country </label>
    <SelectField
      items={["SEK"]}
      disabled={true}
      placeholder={`${wizard.beneficiaryCountry}`}
      id="bank-account-currency"
    />
  </div>
{/if}

<style>
  .radio-container {
    align-items: center;
    display: flex;
    gap: 24px;
    grid-column: 1 / 3;
  }

  .field {
    display: flex;
    flex-direction: column;
  }

  .field label {
    margin-bottom: 16px;
  }
</style>
