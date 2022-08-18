<script lang="ts">
  import PatternedTextField from "$lib/components/patterned-text-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let data: Partial<AddBeneficiaryBankDetailsCombined>;
  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined>;
</script>

<div class="field">
  <label for="accountNumber" class:error={!!errors}>Account Number</label>
  <TextField
    id="accountNumber"
    type="number"
    bind:value={data.accountNumber}
    placeholder="Enter Account number"
    max={99}
    error={!!errors.accountNumber && !data.accountNumber}
  />
</div>
<div class="field">
  <label for="sort-code" class:error={!!errors.sortCode}>Sort Code</label>
  <PatternedTextField
    id="sort-code"
    pattern="99-99-99"
    bind:value={data.sortCode}
    error={!!errors.sortCode && !data.sortCode}
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
