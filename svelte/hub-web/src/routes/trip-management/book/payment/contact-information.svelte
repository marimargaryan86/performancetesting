<script lang="ts" context="module">
  const partialContactDetailsModel = contactDetailsModel.model.deepPartial().extend({
    phone: contactDetailsModel.model.shape.phone.partial(),
    address: contactDetailsModel.model.shape.address.partial().extend({
      street: contactDetailsModel.model.shape.address.shape.street.partial(),
    }),
  });
  export type PartialContactDetailsModel = z.infer<typeof partialContactDetailsModel>;
</script>

<script lang="ts">
  import type { z } from "zod";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { formatCountryOption, formatCountryPhoneOption } from "formatting/location";
  import type { CountryModel } from "models/location";
  import Collapsible from "../../components/collapsible.svelte";
  import {
    contactDetailsModel,
    type ContactDetailsModel,
  } from "integration/junction-mobile-api/schemas/order";

  let countryMap: Map<string, CountryModel>;
  export { countryMap as countries };
  export let contactDetails: PartialContactDetailsModel;
  export let errors: z.ZodFormattedError<ContactDetailsModel> | undefined = undefined;

  let collapsible: Collapsible | undefined;
  let countries = Array.from(countryMap.values());
  let country: CountryModel | undefined = countryMap.get(contactDetails.address.countryCode ?? "");
  let phoneCountry: CountryModel | undefined = countryMap.get(
    contactDetails.phone.countryCode ?? "",
  );

  $: contactDetails = {
    ...contactDetails,
    address: {
      ...contactDetails.address,
      countryCode: country?.code,
    },
    phone: {
      ...contactDetails.phone,
      countryCode: phoneCountry?.phoneCode ? `+${phoneCountry.phoneCode}` : undefined,
    },
  };
  $: if (errors) {
    collapsible?.open();
  }
</script>

<Collapsible bind:this={collapsible} title="Contact information" expandedOnMount>
  <div class="details">
    <div class="phone">
      <SelectField
        options={countries}
        label="Country code"
        placeholder="Select"
        required
        formatter={formatCountryPhoneOption}
        bind:value={phoneCountry}
        error={errors?.phone?.countryCode?._errors}
        dialogMinWidth="240px"
      />
      <TextField
        label="Phone number"
        type="tel"
        placeholder="Enter phone number"
        required
        bind:value={contactDetails.phone.number}
        error={errors?.phone?.number?._errors}
      />
    </div>

    <TextField
      label="Email"
      type="email"
      placeholder="Enter email"
      required
      bind:value={contactDetails.email}
      error={errors?.email?._errors}
    />
    <TextField
      label="Address line 1"
      placeholder="Enter address line 1"
      required
      bind:value={contactDetails.address.street.line1}
      error={errors?.address?.street?.line1?._errors}
    />
    <TextField
      label="Address line 2"
      placeholder="Enter address line 2"
      bind:value={contactDetails.address.street.line2}
      error={errors?.address?.street?.line2?._errors}
    />

    <div class="location">
      <TextField
        label="City"
        placeholder="Enter city"
        required
        bind:value={contactDetails.address.city}
        error={errors?.address?.city?._errors}
      />
      <SelectField
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
        bind:value={contactDetails.address.postalCode}
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
