<script lang="ts">
  import DatePicker from "$lib/components/date-picker/date-picker.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { IndividualBeneficiary } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";

  export let errors: ValidationError<IndividualBeneficiary>;
  export let data: Partial<IndividualBeneficiary>;
</script>

<div class="field">
  <label for="firstName" class:error={!!errors.beneficiaryFirstName && !data.beneficiaryFirstName}>
    First Name
  </label>
  <TextField
    id="firstName"
    type="text"
    bind:value={data.beneficiaryFirstName}
    placeholder="Enter First name"
    error={!!errors.beneficiaryFirstName && !data.beneficiaryFirstName}
  />
</div>
<div class="field">
  <label for="companyName" class:error={!!errors.beneficiaryLastName && !data.beneficiaryLastName}>
    Last Name
  </label>
  <TextField
    id="companyName"
    type="text"
    bind:value={data.beneficiaryLastName}
    placeholder="Enter Last name"
    error={!!errors.beneficiaryLastName && !data.beneficiaryLastName}
  />
</div>
<div class="field">
  <label
    for="beneficiaryDateOfBirth"
    class:error={!!errors.beneficiaryDateOfBirth && !data.beneficiaryDateOfBirth}
  >
    Date of birth
  </label>
  <DatePicker
    span
    id="beneficiaryDateOfBirth"
    bind:start={data.beneficiaryDateOfBirth}
    placeholder="Enter Date of Birth"
    error={!!errors.beneficiaryDateOfBirth && !data.beneficiaryDateOfBirth}
  />
</div>

<style>
  .field {
    display: flex;
    flex-direction: column;
  }

  .field > label.error {
    color: var(--color-red);
  }

  label {
    margin-bottom: 16px;
  }
</style>
