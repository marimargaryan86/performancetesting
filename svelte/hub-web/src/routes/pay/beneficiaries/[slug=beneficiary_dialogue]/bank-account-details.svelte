<script lang="ts" context="module">
  const schema = beneficiaryModel.pick({ currencyCode: true, bankDetails: true });
</script>

<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import { beneficiaryModel, type CreateBeneficiaryModel } from "models/beneficiary";
  import Section from "./section.svelte";
  import type { CurrencyModel } from "models/money";
  import TextField from "components/ui/text-field.svelte";
  import RegularPaymentIcon from "components/icons/regular-payment-icon.svelte";
  import PriorityPaymentIcon from "components/icons/priority-payment-icon.svelte";
  import type { CountryModel } from "models/location";
  import { z } from "zod";
  import { formatError, type FormattedError } from "utils/zod";
  import { updateBeneficiaryData } from "./helpers";
  import { formatCountryOption } from "formatting/location";

  export let data: CreateBeneficiaryModel;
  export let currencies: Map<string, CurrencyModel>;
  export let countries: Map<string, CountryModel>;

  let errors: FormattedError<z.infer<typeof schema>> | undefined = undefined;
  let bankDetails = data.bankDetails ?? {};
  let address = bankDetails.address ?? {};
  let addressLine = address.addressLines?.[0];
  let country = countries.get(data.address?.countryCode ?? "");

  $: address = {
    ...address,
    addressLines: addressLine ? [addressLine] : [],
    countryCode: country?.code,
  };
  $: bankDetails = {
    ...bankDetails,
    address,
    paymentType: bankDetails.paymentType ?? "regular",
    type: bankDetails.type ?? "iban",
    accountType: "checking",
  };
  $: data = { ...data, bankDetails };

  function formatCurrencyOption(code?: string): string {
    const currency = currencies.get(code ?? "");

    return currency ? `${currency.name} (${currency.code})` : "";
  }

  export function validate(): boolean {
    try {
      data = { ...data, ...schema.parse(updateBeneficiaryData(data)) };

      return true;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = formatError<z.infer<typeof schema>>(err);
      }
    }

    return false;
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
      error={errors?.bankDetails?.name}
      bind:value={bankDetails.name}
    />

    <TextField
      label="Bank address"
      required
      placeholder="Enter address"
      error={errors?.bankDetails?.address?.addressLines}
      bind:value={addressLine}
    />

    <SelectField
      label="Country"
      placeholder="Select country"
      options={Array.from(countries.values())}
      formatter={formatCountryOption}
      required
      error={errors?.bankDetails?.address?.countryCode}
      bind:value={country}
    />
    <SelectField
      label="Currency"
      placeholder="Select currency"
      options={Array.from(currencies.values()).map((c) => c.code)}
      formatter={formatCurrencyOption}
      required
      error={errors?.currencyCode}
      bind:value={data.currencyCode}
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
      <label class="option" class:selected={bankDetails.paymentType === "regular"}>
        <RegularPaymentIcon />

        <div>
          <strong class="typography body-large bold">Regular Payment</strong>
          <span class="typography body-small">
            A Domestic or SEPA payment, which is cheaper and avoids correspondent banking fees.
          </span>
        </div>

        <input type="radio" bind:group={bankDetails.paymentType} value="regular" />
      </label>
      <label class="option" class:selected={bankDetails.paymentType === "priority"}>
        <PriorityPaymentIcon />

        <div>
          <strong class="typography body-large bold">Priority Payment</strong>
          <span class="typography body-small">
            An International wire payment, which is the fastest way to transfer funds, but also the
            most expensive.
          </span>
        </div>

        <input type="radio" bind:group={bankDetails.paymentType} value="priority" />
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
      <label class="option typography body-large bold" class:selected={bankDetails.type === "iban"}>
        IBAN

        <input type="radio" bind:group={bankDetails.type} value="iban" />
      </label>
      <label class="option typography body-large bold" class:selected={bankDetails.type === "aba"}>
        Sort code and account no.

        <input type="radio" bind:group={bankDetails.type} value="aba" />
      </label>
    </div>

    <TextField
      label="SWIFT/BIC Code"
      required
      placeholder="Enter SWIFT/BIC Code"
      error={errors?.bankDetails?.bicSwift}
      bind:value={bankDetails.bicSwift}
    />

    {#if bankDetails.type === "iban"}
      <TextField
        label="IBAN Code"
        required
        placeholder="Enter IBAN Code"
        error={errors?.bankDetails && "iban" in errors.bankDetails
          ? errors.bankDetails.iban
          : undefined}
        bind:value={bankDetails.iban}
      />
    {:else}
      <TextField
        label="Sort Code"
        required
        placeholder="00-00-00"
        error={errors?.bankDetails && "aba" in errors.bankDetails
          ? errors.bankDetails.aba
          : undefined}
        bind:value={bankDetails.aba}
      />
      <TextField
        label="Account Number"
        required
        placeholder="00000000"
        error={errors?.bankDetails && "accountNumber" in errors.bankDetails
          ? errors.bankDetails.accountNumber
          : undefined}
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
