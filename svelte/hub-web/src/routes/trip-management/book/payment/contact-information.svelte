<script lang="ts" context="module">
  export const contactDetailsModel: z.ZodType<ContactDetails> = z.object({
    email: z.string().email().trim(),
    address: z.object({
      street: z.object({
        line1: z.string().trim().min(1),
        line2: z.string().trim().min(1).optional(),
      }),
      countryCode: z.string().trim().min(1),
      postalCode: z.string().trim().min(1),
      city: z.string().trim().min(1),
    }),
    phone: z.string().trim().min(1),
  });

  function findCountry(query: string, country?: CountryModel): boolean {
    const queryLower = query.toLowerCase().replaceAll("+", "").trim();

    return Boolean(
      country?.code.toLowerCase().includes(queryLower) ||
        country?.name.toLowerCase().includes(queryLower) ||
        country?.phoneCode.toLowerCase().includes(queryLower),
    );
  }
</script>

<script lang="ts">
  import { z } from "zod";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatCountryOption, formatCountryPhoneOption } from "formatting/location";
  import type { CountryModel } from "models/location";
  import Collapsible from "../../components/collapsible.svelte";
  import type { ContactDetails } from "integration/junction-mobile-api/schemas/journey";

  let countryMap: Map<string, CountryModel>;
  export { countryMap as countries };
  export let data: ContactDetails;
  export let errors: z.ZodFormattedError<ContactDetails> | undefined = undefined;

  let collapsible: Collapsible | undefined;
  let countries = Array.from(countryMap.values());
  let country: CountryModel | undefined = countryMap.get(data.address.countryCode ?? "");

  let phone: {
    country?: CountryModel;
    number: string;
  } = {
    number: "",
  };

  $: if (country) {
    data.address.countryCode = country.code;
  }

  $: if (phone.country && phone.number) {
    data.phone = `+${phone.country.phoneCode}${phone.number}`;
  }

  $: if (errors) {
    collapsible?.open();
  }
</script>

<Collapsible bind:this={collapsible} title="Contact information" expandedOnMount>
  <div class="details">
    <div class="phone">
      <SelectField
        search={findCountry}
        options={countries}
        label="Country code"
        placeholder="Select"
        required
        formatter={formatCountryPhoneOption}
        bind:value={phone.country}
        error={Boolean(errors?.phone?._errors)}
        dialogMinWidth="240px"
      />
      <TextField
        label="Phone number"
        type="tel"
        placeholder="Enter phone number"
        required
        bind:value={phone.number}
        error={errors?.phone?._errors}
      />
    </div>

    <TextField
      label="Email"
      type="email"
      placeholder="Enter email"
      required
      bind:value={data.email}
      error={errors?.email?._errors}
    />
    <TextField
      label="Address line 1"
      placeholder="Enter address line 1"
      required
      bind:value={data.address.street.line1}
      error={errors?.address?.street?.line1?._errors}
    />
    <TextField
      label="Address line 2"
      placeholder="Enter address line 2"
      bind:value={data.address.street.line2}
      error={errors?.address?.street?.line2?._errors}
    />

    <div class="location">
      <TextField
        label="City"
        placeholder="Enter city"
        required
        bind:value={data.address.city}
        error={errors?.address?.city?._errors}
      />
      <SelectField
        search={findCountry}
        direction="up"
        options={countries}
        label="Country"
        placeholder="Select country"
        formatter={formatCountryOption}
        required
        bind:value={country}
        error={errors?.address?.countryCode?._errors}
        dialogMinWidth="240px"
      />
      <TextField
        label="Postcode"
        placeholder="Postcode"
        required
        bind:value={data.address.postalCode}
        error={errors?.address?.postalCode?._errors}
      />
    </div>
  </div>
</Collapsible>

<style>
  .details {
    display: flex;
    flex-flow: column;
    gap: 16px 24px;
  }

  .details :global(.text-field),
  .details :global(.select-field) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --height: 40px;
  }

  .phone {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 24px;
  }

  .location {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .location > :global(.text-field:first-child) {
    grid-column: 1 / -1;
  }
</style>
