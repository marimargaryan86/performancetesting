<script lang="ts" context="module">
  const schema = beneficiaryModel.pick({
    accountId: true,
    companyName: true,
    email: true,
    address: true,
  });
</script>

<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import Section from "./section.svelte";
  import type { CountryModel } from "models/location";
  import { z } from "zod";
  import { updateBeneficiaryData } from "./helpers";
  import { formatCountryOption } from "formatting/location";
  import type { AccountModel } from "integration/junction-pay/schemas/account";
  import {
    beneficiaryModel,
    type CreateBeneficiaryModel,
  } from "integration/junction-pay/schemas/beneficiary.client";

  export let data: CreateBeneficiaryModel;
  export let countries: Map<string, CountryModel>;
  export let accounts: AccountModel[];

  let errors: z.ZodFormattedError<z.infer<typeof schema>> | undefined = undefined;
  let address = data.address ?? {};
  let addressLine = address.addressLines?.[0];
  let country = countries.get(data.address?.countryCode ?? "");

  $: accountIds = accounts.map((a) => a.id);
  $: address = {
    ...address,
    addressLines: addressLine ? [addressLine] : [],
    countryCode: country?.code,
  };
  $: data = { ...data, address };

  function formatAccountOption(id?: string): string {
    return accounts.find((a) => a.id === id)?.name ?? "";
  }

  export function validate(): boolean {
    errors = undefined;

    try {
      data = { ...data, ...schema.parse(updateBeneficiaryData(data)) };

      return true;
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }
    }

    return false;
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
      error={errors?.accountId?._errors}
      bind:value={data.accountId}
    />
    <TextField
      required
      label="Personalised name"
      placeholder="E.g. Air France"
      error={errors?.companyName?._errors}
      bind:value={data.companyName}
    />
    <TextField
      required
      type="email"
      label="Email"
      placeholder="Enter email"
      error={errors?.email?._errors}
      bind:value={data.email}
    />
    <TextField
      required
      label="Address"
      placeholder="Enter address"
      error={errors?.address?.addressLines?._errors}
      bind:value={addressLine}
    />

    <div>
      <TextField
        required
        label="City"
        placeholder="Enter city"
        error={errors?.address?.city?._errors}
        bind:value={address.city}
      />
      <TextField
        required
        label="Postcode"
        placeholder="Enter postcode"
        error={errors?.address?.postalCode?._errors}
        bind:value={address.postalCode}
      />
      <TextField
        label="State"
        placeholder="Enter state"
        error={errors?.address?.state?._errors}
        bind:value={address.state}
      />
      <SelectField
        required
        label="Country"
        placeholder="Select country"
        options={Array.from(countries.values())}
        formatter={formatCountryOption}
        error={errors?.address?.countryCode?._errors}
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
