<script lang="ts">
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import { wizardStore } from "$lib/stores";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined> = {};
  export let data: Partial<AddBeneficiaryBankDetailsCombined>;

  $: wizard = $wizardStore;
</script>

<div class="field">
  <label for="bank-account-currency"> Bank account currency</label>
  <SelectField disabled={true} placeholder={`${wizard.currency}`} id="bank-account-currency" />
</div>
<div class="field">
  <label for="bank-account-country"> Bank account country</label>
  <SelectField
    items={["SEK"]}
    disabled={true}
    placeholder={`${wizard.bankAccountCountry}`}
    id="bank-account-currency"
  />
</div>
<div class="field">
  <label for="accountName" class:error={!!errors.accountName && !data.accountName}
    >Account Name</label
  >
  <TextField
    id="accountName"
    bind:value={data.accountName}
    placeholder="Enter Account Name"
    error={!!errors.accountName && !data.accountName}
  />
</div>

<style>
  .field {
    display: flex;
    flex-direction: column;
  }

  .field label {
    margin-bottom: 16px;
  }
</style>
