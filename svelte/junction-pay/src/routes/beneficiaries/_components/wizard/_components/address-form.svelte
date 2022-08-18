<script lang="ts">
  import TextField from "$lib/components/text-field.svelte";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined> = {};

  export let data: Partial<AddBeneficiaryBankDetailsCombined>;
</script>

<div class="field">
  <label for="addressLine" class:error={!!errors.addressLine && !data.addressLine}
    >Beneficiary address</label
  >
  <TextField
    id="addressLine"
    bind:value={data.addressLine}
    placeholder="Enter Beneficiary address"
    error={!!errors.addressLine && !data.addressLine}
  />
</div>
<div class="field">
  <label for="postCode" class:error={!!errors.postCode && !data.postCode}>Postal Code</label>
  <TextField
    id="postCode"
    bind:value={data.postCode}
    placeholder="Enter post code"
    error={!!errors.postCode && !data.postCode}
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
