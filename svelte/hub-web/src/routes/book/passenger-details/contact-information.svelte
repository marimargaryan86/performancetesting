<script lang="ts" context="module">
  export type ContactInformationData = {
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

  function formatCountryOption(country?: CountryModel): string {
    return country?.name ?? "None";
  }
</script>

<script lang="ts">
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { CountryModel } from "models/location";

  export let countries: Map<string, CountryModel>;
  export let contactInformation: ContactInformationData;

  let country: CountryModel | undefined = undefined;

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
      />
      <TextField
        label="Phone number"
        type="tel"
        placeholder="Enter phone number"
        required
        bind:value={contactInformation.phone.number}
      />
    </div>

    <TextField
      label="Email"
      type="email"
      placeholder="Enter email"
      required
      bind:value={contactInformation.email}
    />
    <TextField
      label="Address line 1"
      placeholder="Enter address line 1"
      required
      bind:value={contactInformation.address.line1}
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
      />
      <SelectField
        direction="up"
        options={Array.from(countries.values())}
        label="Country"
        placeholder="Select country"
        formatter={formatCountryOption}
        required
        bind:value={country}
      />
      <TextField
        label="Postcode"
        placeholder="Postcode"
        required
        bind:value={contactInformation.postcode}
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
