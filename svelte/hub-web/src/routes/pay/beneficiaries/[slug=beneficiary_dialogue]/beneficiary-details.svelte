<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { CreateBeneficiaryModel } from "models/beneficiary";
  import Section from "./section.svelte";
  import type { CountryModel } from "models/location";

  export let data: CreateBeneficiaryModel;
  export let countries: Map<string, CountryModel>;

  let country = data.address?.countryCode ? countries.get(data.address.countryCode) : undefined;
  let city = data.address?.city;
  let address = data.address?.addressLines?.[0];

  $: data = {
    ...data,
    address: {
      ...data.address,
      countryCode: country?.code,
      city,
      addressLines: address ? [address] : [],
    },
  };

  function formatOption(value?: CountryModel): string {
    return value?.name ? `${value.name} (${value.code})` : "";
  }
</script>

<Section
  title="Beneficiary Details"
  intro="Company info"
  description="Provide the company information"
>
  <form>
    <TextField
      label="Personalised name"
      placeholder="E.g. Air France"
      bind:value={data.bankAccountHolderName}
    />
    <SelectField
      label="Country"
      placeholder="Select the beneficiary's country"
      options={Array.from(countries.values())}
      formatter={formatOption}
      bind:value={country}
    />
    <TextField label="City" placeholder="Enter the city of the beneficiary" bind:value={city} />
    <TextField
      label="Address"
      placeholder="Enter the address of the beneficiary"
      bind:value={address}
    />
  </form>
</Section>
