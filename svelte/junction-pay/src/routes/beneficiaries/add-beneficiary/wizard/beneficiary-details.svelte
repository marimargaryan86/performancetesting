<script lang="ts">
  import countriesData from "$content/countries";
  import currenciesData from "$content/currencies";
  import Button from "$lib/components/button.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type {
    BeneficiaryDetailsData,
    BeneficiaryDetailsError,
  } from "$models/beneficiary-models/models";
  import { validateBeneficiaryDetails } from "$models/beneficiary-models/validators";
  import Navigation from "./navigation.svelte";

  export let data: Partial<BeneficiaryDetailsData>;
  export let goToNext: () => void;

  let errors: BeneficiaryDetailsError | undefined = undefined;

  const countries = countriesData;
  const currencies = currenciesData;

  async function submit(): Promise<void> {
    errors = validateBeneficiaryDetails(data);

    if (!errors) {
      goToNext();
    }
  }
</script>

<form class="beneficiary-details" on:submit|preventDefault={submit}>
  <div class="field">
    <label for="nickname" class:error={errors?.nickname}>Beneficiary nickname</label>
    <TextField
      id="nickname"
      bind:value={data.nickname}
      placeholder="Enter nickname"
      error={errors?.nickname?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="beneficiary-country" class:error={errors?.addressCountry}>
      Beneficiary country
    </label>
    <SelectField
      bind:value={data.addressCountry}
      displayValue={(value) => value?.name ?? ""}
      items={countries}
      placeholder="Select country"
      id="beneficiary-country"
      error={errors?.addressCountry?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="bank-account-country" class:error={errors?.accountCountry}>
      Bank account country
    </label>
    <SelectField
      bind:value={data.accountCountry}
      displayValue={(value) => value?.name ?? ""}
      items={countries}
      placeholder="Select country"
      id="bank-account-country"
      error={errors?.accountCountry?.join(", ")}
    />
  </div>

  <div class="field">
    <label for="currency" class:error={errors?.accountCurrency}>Currency</label>
    <SelectField
      bind:value={data.accountCurrency}
      displayValue={(data) => data?.code ?? ""}
      items={currencies}
      placeholder="Select currency"
      id="currency"
      error={errors?.accountCurrency?.join(", ")}
    />
  </div>

  <Navigation>
    <Button type="submit" slot="next">Next</Button>
  </Navigation>
</form>

<style>
  .beneficiary-details {
    display: grid;
    gap: 36px;
    grid-template-columns: 1fr 1fr;
  }

  .field > label {
    display: block;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .field > :global(.text-field) {
    padding: 0 18px;
  }

  .beneficiary-details > :global(.navigation) {
    grid-column: 1 / -1;
  }

  .field > :global(.text-field),
  .field > :global(.select-field.select-field) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    width: 100%;
  }

  .error {
    color: var(--color-red);
  }
</style>
