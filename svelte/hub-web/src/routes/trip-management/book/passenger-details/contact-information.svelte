<script lang="ts" context="module">
  export type PartialContactInformationData = {
    phone: {
      code?: string;
      number?: string;
    };
    email?: string;
    address: {
      line1?: string;
      line2?: string;
    };
    city?: string;
    countryCode?: string;
    postcode?: string;
  };

  export const contactInformationData = z.object({
    phone: z.object({
      code: z.string({ required_error: "Country code required" }),
      number: string({ required_error: "Phone number required" }),
    }),
    email: z.string().email({ message: "Invalid email address" }),
    address: z.object({
      line1: z.string({ required_error: "Street address required" }),
      line2: string().optional(),
    }),
    city: z.string({ required_error: "City required" }),
    countryCode: z.string({ required_error: "Country redquired" }),
    postcode: z.string({ required_error: "Post code required" }),
  });

  export type ContactInformationData = z.infer<typeof contactInformationData>;
</script>

<script lang="ts">
  import { string, z } from "zod";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatCountryOption } from "formatting/location";
  import type { CountryModel } from "models/location";

  export let countries: Map<string, CountryModel>;
  export let contactInformation: PartialContactInformationData;
  export let errors: z.ZodFormattedError<ContactInformationData> | undefined = undefined;

  let country: CountryModel | undefined = countries.get(contactInformation.countryCode ?? "");

  $: contactInformation = {
    ...contactInformation,
    countryCode: country?.code,
  };
</script>

<div class="contact-information">
  <h2 class="typography title-large bold">Agent's contact information</h2>

  <div class="details">
    <div class="phone">
      <SelectField
        options={["+34"]}
        label="Country code"
        placeholder="Select"
        required
        bind:value={contactInformation.phone.code}
        error={errors?.phone?.code?._errors}
      />
      <TextField
        label="Phone number"
        type="tel"
        placeholder="Enter phone number"
        required
        bind:value={contactInformation.phone.number}
        error={errors?.phone?.number?._errors}
      />
    </div>

    <TextField
      label="Email"
      type="email"
      placeholder="Enter email"
      required
      bind:value={contactInformation.email}
      error={errors?.email?._errors}
    />
    <TextField
      label="Address line 1"
      placeholder="Enter address line 1"
      required
      bind:value={contactInformation.address.line1}
      error={errors?.address?.line1?._errors}
    />
    <TextField
      label="Address line 2"
      placeholder="Enter address line 2"
      bind:value={contactInformation.address.line2}
    />

    <div class="location">
      <TextField
        label="City"
        placeholder="Enter city"
        required
        bind:value={contactInformation.city}
        error={errors?.city?._errors}
      />
      <SelectField
        direction="up"
        options={Array.from(countries.values())}
        label="Country"
        placeholder="Select country"
        formatter={formatCountryOption}
        required
        bind:value={country}
        error={errors?.countryCode?._errors}
      />
      <TextField
        label="Postcode"
        placeholder="Postcode"
        required
        bind:value={contactInformation.postcode}
        error={errors?.postcode?._errors}
      />
    </div>
  </div>
</div>

<style>
  .contact-information {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 40px 80px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .details {
    display: flex;
    flex-flow: column;
    gap: 24px;
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
    grid-template-columns: 1fr 1fr 112px;
    gap: 24px;
  }
</style>
