<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import type { CreateBeneficiaryModel } from "models/beneficiary";
  import Section from "./section.svelte";
  import type { CurrencyModel } from "models/money";
  import TextField from "components/ui/text-field.svelte";
  import RegularPaymentIcon from "components/icons/regular-payment-icon.svelte";
  import PriorityPaymentIcon from "components/icons/priority-payment-icon.svelte";
  import type { CountryModel } from "models/location";

  export let data: CreateBeneficiaryModel;
  export let currencies: Map<string, CurrencyModel>;
  export let countries: Map<string, CountryModel>;

  let country = data.bankDetails?.address?.countryCode
    ? countries.get(data.bankDetails.address.countryCode)
    : undefined;
  let currency = data.currencyCode ? currencies.get(data.currencyCode) : undefined;
  let bankDetails = data.bankDetails ?? { paymentTypes: "regular", type: "iban" };
  let address = bankDetails.address ?? {};

  $: address.countryCode = country?.code;
  $: bankDetails.type = bankDetails.paymentTypes === "regular" ? "aba" : bankDetails.type;
  $: bankDetails.address = address;
  $: data = {
    ...data,
    bankDetails,
    currencyCode: currency?.code,
  };

  function formatCountryOption(value?: { name: string; code: string }): string {
    return value?.name ?? "";
  }

  function formatCurrencyOption(value?: CurrencyModel): string {
    return value ? `${value.name} (${value.code})` : "";
  }
</script>

<Section
  title="Bank Account Details"
  intro="Location and currency"
  description="Provide the company company bank information"
>
  <form>
    <SelectField
      label="Country"
      placeholder="Select bank account country"
      options={Array.from(countries.values())}
      formatter={formatCountryOption}
      bind:value={country}
    />
    <SelectField
      label="Currency"
      placeholder="Select bank account currency"
      options={Array.from(currencies.values())}
      formatter={formatCurrencyOption}
      bind:value={currency}
    />
  </form>
</Section>

<hr class="divider" />

<Section
  intro="Payment Type"
  description="Select the payment method through which you want to make your transfers."
>
  <form>
    <div class="options">
      <label class="option" class:selected={bankDetails.paymentTypes === "regular"}>
        <RegularPaymentIcon />

        <div>
          <strong class="typography body-large bold">Regular Payment</strong>
          <span class="typography body-small">
            A Domestic or SEPA payment, which is cheaper and avoids correspondent banking fees.
          </span>
        </div>

        <input type="radio" bind:group={bankDetails.paymentTypes} value="regular" />
      </label>
      <label class="option" class:selected={bankDetails.paymentTypes === "priority"}>
        <PriorityPaymentIcon />

        <div>
          <strong class="typography body-large bold">Priority Payment</strong>
          <span class="typography body-small">
            An International wire payment, which is the fastest way to transfer funds, but also the
            most expensive.
          </span>
        </div>

        <input type="radio" bind:group={bankDetails.paymentTypes} value="priority" />
      </label>
    </div>
  </form>
</Section>

<hr class="divider" />

<Section
  intro="Banking information"
  description="Select the type of banking information you wish to use and fill in the fields."
>
  <form>
    {#if bankDetails.paymentTypes === "priority"}
      <div class="options">
        <label
          class="option typography body-large bold"
          class:selected={bankDetails.type === "iban"}
        >
          SWIFT/BIC

          <input type="radio" bind:group={bankDetails.type} value="iban" />
        </label>
        <label
          class="option typography body-large bold"
          class:selected={bankDetails.type === "aba"}
        >
          Sort code

          <input type="radio" bind:group={bankDetails.type} value="aba" />
        </label>
      </div>

      <TextField label="Company Name" placeholder="Full name of the company holding the account" />

      {#if bankDetails.type === "iban"}
        <TextField label="IBAN Code" placeholder="Enter the IBAN code of the beneficiary bank" />
        <TextField
          label="SWIFT/BIC Code"
          placeholder="Enter the SWIFT/BIC code of the beneficiary bank"
          bind:value={bankDetails.bicSwift}
        />
      {/if}
    {/if}

    <TextField
      label="Sort Code"
      placeholder="Enter the sort code"
      helpText="Only one Sort Code value is permitted per beneficiary. Please note that changing the Sort Code value for one payment type will amend it for both."
    />

    {#if bankDetails.type === "aba"}
      <TextField
        label="Account Number"
        placeholder="Enter the account number"
        bind:value={bankDetails.accountNumber}
      />
    {/if}
  </form>
</Section>

<style>
  .divider {
    align-self: center;
    width: 100%;
    max-width: 914px;
    margin: 0;
    border: 0;
    border-bottom: var(--color-common-line-soft) 1px solid;
  }

  .options {
    display: flex;
    gap: 24px;
  }

  .option {
    display: flex;
    flex-grow: 1;
    gap: 8px;
    justify-content: center;
    padding: 16px;
    border: var(--color-common-line-medium) 1px solid;
    border-radius: 8px;
    cursor: pointer;
    transition: border 250ms ease, box-shadow 250ms ease, background-color 250ms ease;
    user-select: none;
  }

  .option > :global(svg) {
    flex-shrink: 0;
  }

  .option.selected {
    background-color: var(--color-main-primary-50);
    border-color: var(--color-main-primary-500);
    box-shadow: 0 0 0 1px var(--color-main-primary-500) inset;
  }

  .option > div {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .option > div > span {
    color: var(--color-common-light-medium);
  }

  .option > input {
    display: none;
  }
</style>
