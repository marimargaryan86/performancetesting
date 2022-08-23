<script lang="ts">
  import DatePicker from "$lib/components/date-picker/date-picker.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { EntityDetailsData, EntityDetailsError } from "$models/beneficiary-models/models";

  export let data: Partial<EntityDetailsData>;
  export let errors: EntityDetailsError | undefined = undefined;
</script>

{#if data.type === "company"}
  <div class="field">
    <label for="company-name" class:error={errors?.companyName}>Company name</label>
    <TextField
      id="company-name"
      bind:value={data.companyName}
      placeholder="Enter company name"
      error={errors?.companyName?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="registration-date" class:error={errors?.companyRegistrationDate}>
      Date of registration
    </label>

    <DatePicker
      end={undefined}
      id="registration-date"
      bind:start={data.companyRegistrationDate}
      placeholder="Enter date of registration"
      error={errors?.companyRegistrationDate?.join(", ")}
    />
  </div>
{:else if data.type === "individual"}
  <div class="field">
    <label for="first-name" class:error={errors?.individualFirstName}>First name</label>
    <TextField
      id="first-name"
      type="text"
      bind:value={data.individualFirstName}
      placeholder="Enter first name"
      error={errors?.individualFirstName?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="last-name" class:error={errors?.individualLastName}>Last name</label>
    <TextField
      id="last-name"
      type="text"
      bind:value={data.individualLastName}
      placeholder="Enter last name"
      error={errors?.individualLastName?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="birth-date" class:error={errors?.individualBirthDate}>Date of birth</label>
    <DatePicker
      id="birth-date"
      bind:start={data.individualBirthDate}
      placeholder="Enter date of birth"
      error={errors?.individualBirthDate?.join(", ")}
    />
  </div>
{/if}

<style>
  .field > label {
    display: block;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .field > :global(.text-field),
  .field > :global(.date-picker) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    width: 100%;
  }

  .field > :global(.text-field),
  .field > :global(.date-picker > .text-field) {
    padding: 0 18px;
  }

  .error {
    color: var(--color-red);
  }
</style>
