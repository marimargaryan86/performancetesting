<script lang="ts">
  import countryData from "$content/countries";
  import currencyData from "$content/currencies";
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import type { AccountDetailsData, AccountDetailsError } from "$models/beneficiary-models/models";

  export let data: Partial<AccountDetailsData> = {};
  export let errors: AccountDetailsError | undefined = undefined;

  const currencies = currencyData;
  const countries = countryData;
</script>

<div class="field">
  <label for="bank-account-currency" class:error={!!errors?.accountCurrency}>
    Bank account currency
  </label>
  <SelectField
    disabled
    items={currencies}
    bind:value={data.accountCurrency}
    displayValue={(value) => value?.code ?? ""}
    placeholder="Select currency"
    id="bank-account-currency"
    error={errors?.accountCurrency?.join(", ")}
  />
</div>

<div class="field">
  <label for="bank-account-country" class:error={!!errors?.accountCountry}>
    Bank account country
  </label>
  <SelectField
    disabled
    items={countries}
    bind:value={data.accountCountry}
    displayValue={(value) => value?.name ?? ""}
    placeholder="Select country"
    id="bank-account-country"
    error={errors?.accountCountry?.join(", ")}
  />
</div>

<div class="field">
  <label for="account-city" class:error={errors?.accountCity}>Bank account city</label>
  <TextField
    id="account-city"
    bind:value={data.accountCity}
    placeholder="Enter city name"
    error={errors?.accountCity?.join(", ")}
  />
</div>

<div class="field">
  <label for="account-holder-name" class:error={errors?.accountHolderName}>
    Account holder Name
  </label>
  <TextField
    id="account-holder-name"
    bind:value={data.accountHolderName}
    placeholder="Enter account holder name"
    error={errors?.accountHolderName?.join(", ")}
  />
</div>

<div class="field">
  <label for="account-number" class:error={errors?.accountNumber}> Account number </label>
  <TextField
    id="account-number"
    bind:value={data.accountNumber}
    placeholder="Enter account number"
    error={errors?.accountNumber?.join(", ")}
  />
</div>

<style>
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

  .field > :global(.text-field),
  .field > :global(.select-field.select-field) {
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    width: 100%;
  }

  .field > :global(.select-field > .head > .text-field) {
    padding: 0 18px;
  }

  .error {
    color: var(--color-red);
  }
</style>
