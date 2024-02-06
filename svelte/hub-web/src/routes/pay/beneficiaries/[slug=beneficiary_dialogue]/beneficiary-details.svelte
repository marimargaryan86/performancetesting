<script lang="ts">
  import SelectField from "~/components/ui/select-field.svelte";
  import TextField from "~/components/ui/text-field.svelte";
  import Section from "./section.svelte";
  import type { CountryModel } from "~/models/location";
  import { formatCountryOption } from "~/formatting/location";
  import type { Account } from "~/integration/junction-hub-api/schemas/account";
  import type { BeneficiaryPut } from "~/integration/junction-hub-api/schemas/beneficiary";
  import countryData from "~/data/country-data";
  import { getLocaleData } from "~/i18n";

  export let data: BeneficiaryPut;
  export let accounts: Account[];

  const i18n = getLocaleData();

  let country = countryData.mapping[data.address?.countryCode ?? ""];

  $: accountIds = accounts.map((a) => a.id);
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

  function formatAccountOption(id?: string): string {
    return accounts.find((a) => a.id === id)?.name ?? "";
  }

  export function validate(): boolean {
    return true;
  }
</script>

<Section
  title="Beneficiary Details"
  intro="Company info"
  description="Provide the company information"
>
  <form>
    <SelectField
      required
      label="Account"
      placeholder="Select account"
      options={accountIds}
      formatter={formatAccountOption}
      bind:value={data.accountId}
    />
    <TextField
      required
      label="Personalised name"
      placeholder="E.g. Air France"
      bind:value={data.bankAccountHolderName}
    />
    <TextField
      required
      type="email"
      label="Email"
      placeholder="Enter email"
      bind:value={data.email}
    />
    <TextField
      required
      label="Address"
      placeholder="Enter address"
      bind:value={data.address.street.line1}
    />

    <div>
      <TextField required label="City" placeholder="Enter city" bind:value={data.address.city} />
      <TextField
        required
        label="Postcode"
        placeholder="Enter postcode"
        bind:value={data.address.postalCode}
      />
      <TextField label="State" placeholder="Enter state" bind:value={data.address.state} />
      <SelectField
        required
        label="Country"
        placeholder="Select country"
        options={countryData.list}
        formatter={formatCountryOption.bind(formatCountryOption, $i18n)}
        bind:value={country}
      />
    </div>
  </form>
</Section>

<style>
  div {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
</style>
