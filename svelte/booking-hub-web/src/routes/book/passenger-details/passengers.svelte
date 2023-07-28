<script lang="ts">
  import TextField from "components/ui/text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import type { Passenger } from "../passenger";

  export let passengers: Passenger[];

  const genders = ["Male", "Female"];
  const titles = ["Mr", "Mrs", "Ms"];
</script>

{#each passengers as passenger, index (passenger)}
  <div class="passenger">
    <h3 class="current-passenger">Passenger {index + 1}</h3>
    <p class="typography title-medium passenger-type">{passenger.type}</p>
    <div class="passenger-form">
      <SelectField
        label="Select title"
        required
        placeholder="Select"
        options={titles}
        bind:value={passenger.title}
      />
      <div />
      <TextField
        class="firstname"
        type="text"
        bind:value={passenger.firstName}
        placeholder="Enter first name"
        label="First name"
        required
      />
      <TextField
        class="lastname"
        type="text"
        bind:value={passenger.lastName}
        placeholder="Enter last name"
        label="Last name"
        required
      />
      <TextField
        class="birth"
        type="text"
        bind:value={passenger.birth}
        placeholder="dd/mm/yyyy"
        mask="##/##/####"
        limit={8}
        label="Birthday"
        required
      />
      <SelectField
        label="Gender"
        placeholder="Select"
        options={genders}
        bind:value={passenger.gender}
      />
    </div>
  </div>
{/each}

<style>
  .passenger {
    width: 100%;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .passenger-type {
    margin-bottom: 24px;
    font-weight: 400;
  }

  .passenger-form {
    display: grid;
    grid-template: repeat(3, 1fr) / repeat(2, 1fr);
    gap: 16px;
  }

  .passenger-form > :global(.text-field .wrapper) {
    height: 40px;
  }

  .passenger-form > :global(.select-field .wrapper) {
    height: 40px;
  }

  .passenger-form > :global(.select-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .passenger-form > :global(.text-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  h3 {
    margin-bottom: 8px;
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }
</style>
