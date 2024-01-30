<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import Section from "./section.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { CountryModel } from "models/location";
  import { formatCountryOption } from "formatting/location";
  import type { BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
  import countryData from "data/country-data";
  import currencyData from "data/currency-data";
  import Icon from "components/icons/icon.svelte";
  import { getLocaleData } from "i18n";

  export let data: BeneficiaryPut;

  const i18n = getLocaleData();

  let country = countryData.mapping[data.address?.countryCode ?? ""];

  $: data = updateCountry(country);

  function updateCountry(nextCountry?: CountryModel): BeneficiaryPut {
    if (!nextCountry) {
      return data;
    }

    return {
      ...data,
      address: {
        ...data.address,
        countryCode: nextCountry.code,
      },
    };
  }

  function formatCurrencyOption(code?: string): string {
    const currency = currencyData.mapping[code ?? ""];

    return currency ? `${currency.name} (${currency.code})` : "";
  }

  export function validate(): boolean {
    return true;
  }
</script>

<Section
  title="Bank Account Details"
  intro="Bank name and address"
  description="Provide the bank name and address"
>
  <form>
    <TextField
      label="Bank name"
      required
      placeholder="Enter bank name"
      bind:value={data.bankDetails.name}
    />

    <TextField
      label="Bank address"
      required
      placeholder="Enter address"
      bind:value={data.bankDetails.address.street.line1}
    />

    <SelectField
      label="Country"
      placeholder="Select country"
      options={countryData.list}
      formatter={formatCountryOption.bind(formatCountryOption, $i18n)}
      required
      bind:value={country}
    />
    <SelectField
      label="Currency"
      placeholder="Select currency"
      options={Object.keys(currencyData.mapping)}
      formatter={formatCurrencyOption}
      required
      bind:value={data.currencyId}
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
      <label class="option" class:selected={data.bankDetails.paymentType === "regular"}>
        <Icon variant="regular-payment" />

        <div>
          <strong typography="body-large" weight="bold">Regular Payment</strong>
          <span typography="body-small">
            A Domestic or SEPA payment, which is cheaper and avoids correspondent banking fees.
          </span>
        </div>

        <input type="radio" bind:group={data.bankDetails.paymentType} value="regular" />
      </label>
      <label class="option" class:selected={data.bankDetails.paymentType === "priority"}>
        <Icon variant="priority-payment" />

        <div>
          <strong typography="body-large" weight="bold">Priority Payment</strong>
          <span typography="body-small">
            An International wire payment, which is the fastest way to transfer funds, but also the
            most expensive.
          </span>
        </div>

        <input type="radio" bind:group={data.bankDetails.paymentType} value="priority" />
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
    <div class="options">
      <label
        class="option"
        typography="body-large"
        weight="bold"
        class:selected={data.bankDetails.type === "iban"}
      >
        IBAN

        <input type="radio" bind:group={data.bankDetails.type} value="iban" />
      </label>
      <label
        class="option"
        typography="body-large"
        weight="bold"
        class:selected={data.bankDetails.type === "aba"}
      >
        Sort code and account no.

        <input type="radio" bind:group={data.bankDetails.type} value="aba" />
      </label>
    </div>

    <TextField
      label="SWIFT/BIC Code"
      required
      placeholder="Enter SWIFT/BIC Code"
      bind:value={data.bankDetails.bicSwift}
    />

    {#if data.bankDetails.type === "iban"}
      <TextField
        label="IBAN Code"
        required
        placeholder="Enter IBAN Code"
        bind:value={data.bankDetails.iban}
      />
    {:else}
      <TextField
        label="Sort Code"
        required
        placeholder="00-00-00"
        bind:value={data.bankDetails.aba}
      />
      <TextField
        label="Account Number"
        required
        placeholder="00000000"
        bind:value={data.bankDetails.accountNumber}
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
    transition:
      border 250ms ease,
      box-shadow 250ms ease,
      background-color 250ms ease;
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
