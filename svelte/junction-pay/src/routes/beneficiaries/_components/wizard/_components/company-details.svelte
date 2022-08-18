<script lang="ts">
  import DatePicker from "$lib/components/date-picker/date-picker.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { CompanyBeneficiary } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let errors: ValidationError<CompanyBeneficiary>;
  export let data: Partial<CompanyBeneficiary>;
</script>

<div class="field">
  <label
    for="beneficiaryEntityName"
    class:error={!!errors.beneficiaryEntityName && !data.beneficiaryEntityName}
  >
    Company name
  </label>
  <TextField
    id="beneficiaryEntityName"
    bind:value={data.beneficiaryEntityName}
    placeholder="Enter Company name"
    error={!!errors.beneficiaryEntityName && !data.beneficiaryEntityName}
  />
</div>
<div class="field">
  <label
    for="beneficiaryDateOfBirth"
    class:error={!!errors.beneficiaryDateOfBirth && !data.beneficiaryDateOfBirth}
  >
    Date of registration
  </label>
  <DatePicker
    end={undefined}
    id="beneficiaryDateOfBirth"
    bind:start={data.beneficiaryDateOfBirth}
    placeholder="Enter Date of registration"
    error={!!errors.beneficiaryDateOfBirth && !data.beneficiaryDateOfBirth}
  />
</div>

<style>
  .field {
    display: flex;
    flex-direction: column;
  }

  label {
    margin-bottom: 16px;
  }
</style>
