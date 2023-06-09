<script lang="ts" context="module">
  const schema = beneficiaryModel
    .pick({
      companyName: true,
      email: true,
    })
    .extend({
      address: beneficiaryModel._def.shape().address.required(),
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

  export let data: CreateBeneficiaryModel;
  export let countries: Map<string, CountryModel>;

  let errors: FormattedError<z.infer<typeof schema>>;
  let address = data.address ?? {};
  let addressLine = address.addressLines?.[0];

  $: address = { ...address, addressLines: addressLine ? [addressLine] : [] };
  $: data = { ...data, address };

  function formatOption(code?: string): string {
    return countries.get(code ?? "")?.name ?? "";
  }

  export function validate(): boolean {
    const nextData: CreateBeneficiaryModel = {
      ...data,
      companyName: data.companyName?.trim(),
      email: data.email?.trim(),
      address: {
        ...data.address,
        addressLines: data.address?.addressLines?.map((al) => al.trim()),
        city: data.address?.city?.trim(),
        postalCode: data.address?.postalCode?.trim(),
        state: data.address?.state?.trim(),
      },
    };

    try {
      data = { ...data, ...schema.parse(nextData) };

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
    <TextField
      required
      label="Personalised name"
      placeholder="E.g. Air France"
      bind:value={data.companyName}
      error={errors?.companyName}
    />
    <TextField
      required
      type="email"
      label="Email"
      placeholder="Enter email"
      bind:value={data.email}
      error={errors?.email}
    />
    <TextField
      required
      label="Address"
      placeholder="Enter address"
      bind:value={addressLine}
      error={errors?.address?.addressLines}
    />

    <div>
      <TextField
        required
        label="City"
        placeholder="Enter city"
        bind:value={address.city}
        error={errors?.address?.city}
      />
      <TextField
        required
        label="Postcode"
        placeholder="Enter postcode"
        bind:value={address.postalCode}
        error={errors?.address?.postalCode}
      />
      <TextField
        required
        label="State"
        placeholder="Enter state"
        bind:value={address.state}
        error={errors?.address?.state}
      />
      <SelectField
        required
        label="Country"
        placeholder="Select country"
        options={Array.from(countries.values()).map((c) => c.code)}
        formatter={formatOption}
        bind:value={address.countryCode}
        error={errors?.address?.countryCode}
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
