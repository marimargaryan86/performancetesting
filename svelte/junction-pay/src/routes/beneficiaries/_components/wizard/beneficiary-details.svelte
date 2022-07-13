<script lang="ts">
  import countriesData from "$content/countries";
  import currenciesData from "$content/currencies";
  import Button from "$lib/components/button.svelte";
  import Radio from "$lib/components/radio.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import Spinner from "$lib/components/spinner.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import utils from "$lib/utils";
  import type { AddBeneficiaryDetailsData } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";
  import instances from "$services/instances";
  import { scale } from "svelte/transition";

  export let goToNext: () => void;

  let errors: ValidationError<AddBeneficiaryDetailsData> = {};

  const data: Partial<AddBeneficiaryDetailsData> = {
    nickname: "",
    beneficiaryCountry: undefined,
    bankAccountCountry: undefined,
    currency: undefined,
    holderName: "",
    type: "company",
  };

  const { beneficiary: service } = instances;
  const { pending, func: addBeneficiaryDetails } = utils.pendableCall(
    service.addBeneficiaryDetails.bind(service),
    false,
  );
  const countries = countriesData.map((country) => ({ ...country, toString: () => country.name }));
  const currencies = currenciesData.map((currency) => ({
    ...currency,
    toString: () => currency.code,
  }));

  async function submit(): Promise<void> {
    if ($pending) {
      return;
    }

    errors = {};

    try {
      await addBeneficiaryDetails(data as AddBeneficiaryDetailsData);

      goToNext();
    } catch (e) {
      errors = e as typeof errors;
    }
  }
</script>

<form class="beneficiary-details" on:submit|preventDefault={submit}>
  <div class="field">
    <label for="nickname" class:error={!!errors.nickname}>Beneficiary nickname</label>
    <TextField
      id="nickname"
      bind:value={data.nickname}
      placeholder="Enter nickname"
      error={!!errors.nickname}
    />
  </div>

  <div class="field">
    <label for="beneficiary-country" class:error={!!errors.beneficiaryCountry}>
      Beneficiary country
    </label>
    <SelectField
      bind:value={data.beneficiaryCountry}
      items={countries}
      placeholder="Select country"
      id="beneficiary-country"
      error={!!errors.beneficiaryCountry}
    />
  </div>

  <div class="field">
    <label for="bank-account-country" class:error={!!errors.bankAccountCountry}>
      Bank account country
    </label>
    <SelectField
      bind:value={data.bankAccountCountry}
      items={countries}
      placeholder="Select country"
      id="bank-account-country"
      error={!!errors.bankAccountCountry}
    />
  </div>

  <div class="field">
    <label for="currency" class:error={!!errors.currency}>Currency</label>
    <SelectField
      bind:value={data.currency}
      items={currencies}
      placeholder="Select currency"
      id="currency"
      error={!!errors.currency}
    />
  </div>

  <div class="field">
    <label for="holder-name" class:error={!!errors.holderName}>Account holder name</label>
    <TextField
      id="holder-name"
      bind:value={data.holderName}
      placeholder="Enter holder name"
      error={!!errors.holderName}
    />
  </div>

  <fieldset>
    <legend>Beneficiary type</legend>
    <Radio value="company" bind:group={data.type} id="company" />
    <label for="company">Company</label>

    <Radio value="individual" bind:group={data.type} id="individual" />
    <label for="individual">Individual</label>
  </fieldset>

  <span />

  <Button type="submit">
    Next

    {#if $pending}
      <Spinner transition={{ func: scale, params: { duration: 150 } }} />
    {/if}
  </Button>
</form>

<style>
  .beneficiary-details {
    display: grid;
    gap: 60px 36px;
    grid-template-columns: 1fr 1fr;
  }

  fieldset > label {
    font-size: 18px;
    margin-left: 4px;
  }

  .field > label,
  legend {
    display: block;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .field > label.error {
    color: var(--color-red);
  }

  legend {
    margin-bottom: 32px;
  }

  fieldset > :global(*) {
    vertical-align: middle;
  }

  .beneficiary-details > :global(button) {
    background-color: var(--color-orange);
    font-size: 20px;
    height: 56px;
    justify-self: flex-end;
    width: 310px;
  }

  .field > :global(.text-field) {
    padding: 0 18px;
  }

  .beneficiary-details > :global(button > .spinner) {
    margin-left: 8px;
    vertical-align: middle;
  }

  fieldset > :global(.radio:not(:first-of-type)) {
    margin-left: 50px;
  }

  .field > :global(.text-field.text-field),
  .field > :global(.select-field.select-field) {
    border-color: transparent;
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    width: 100%;
  }
</style>
