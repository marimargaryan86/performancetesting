<script lang="ts">
  import TextField from "$lib/components/text-field.svelte";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let data: Partial<AddBeneficiaryBankDetailsCombined>;
  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined>;
  export let types: string[];
</script>

{#if types.includes("swift")}
  <div class="field">
    <label for="companyName" class:error={!!errors}>BIC/SWIFT</label>
    <TextField
      id="companyName"
      bind:value={data.bic}
      placeholder="Enter BIC/SWIFT"
      error={!!errors.bic && !data.bic}
    />
  </div>
  <div class="field">
    <label for="beneficiaryDateOfBirth" class:error={!!errors}>IBAN</label>
    <TextField
      id="companyName"
      bind:value={data.iban}
      placeholder="Enter IBAN"
      error={!!errors.iban && !data.iban}
    />
  </div>
{/if}

<style>
  .field {
    display: flex;
    flex-direction: column;
  }

  .field label {
    margin-bottom: 16px;
  }
</style>
