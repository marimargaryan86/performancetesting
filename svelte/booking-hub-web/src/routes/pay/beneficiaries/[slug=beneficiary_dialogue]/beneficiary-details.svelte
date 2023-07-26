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
  import { beneficiaryModel, type CreateBeneficiaryModel } from "models/beneficiary";
  import Section from "./section.svelte";
  import type { CountryModel } from "models/location";
  import { z } from "zod";
  import { formatError, type FormattedError } from "utils/zod";
  import { updateBeneficiaryData } from "./helpers";
  import type { AccountModel } from "models/account";

  export let data: CreateBeneficiaryModel;
  export let countries: Map<string, CountryModel>;
  export let accounts: AccountModel[];

  let errors: FormattedError<z.infer<typeof schema>> | undefined = undefined;
  let address = data.address ?? {};
  let addressLine = address.addressLines?.[0];

  $: accountIds = accounts.map((a) => a.id);
  $: address = { ...address, addressLines: addressLine ? [addressLine] : [] };
  $: data = { ...data, address };

  function formatCountryOption(code?: string): string {
    return countries.get(code ?? "")?.name ?? "";
  }

  function formatAccountOption(id?: string): string {
    return accounts.find((a) => a.id === id)?.name ?? "";
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
      error={errors?.accountId}
      bind:value={data.accountId}
    />
    <TextField
      required
      label="Personalised name"
      placeholder="E.g. Air France"
      error={errors?.companyName}
      bind:value={data.companyName}
    />
    <TextField
      required
      type="email"
      label="Email"
      placeholder="Enter email"
      error={errors?.email}
      bind:value={data.email}
    />
    <TextField
      required
      label="Address"
      placeholder="Enter address"
      error={errors?.address?.addressLines}
      bind:value={addressLine}
    />

    <div>
      <TextField
        required
        label="City"
        placeholder="Enter city"
        error={errors?.address?.city}
        bind:value={address.city}
      />
      <TextField
        required
        label="Postcode"
        placeholder="Enter postcode"
        error={errors?.address?.postalCode}
        bind:value={address.postalCode}
      />
      <TextField
        label="State"
        placeholder="Enter state"
        error={errors?.address?.state}
        bind:value={address.state}
      />
      <SelectField
        required
        label="Country"
        placeholder="Select country"
        options={Array.from(countries.values()).map((c) => c.code)}
        formatter={formatCountryOption}
        error={errors?.address?.countryCode}
        bind:value={address.countryCode}
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
