<script lang="ts">
  import type { z } from "zod";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import { formatCountryOption, formatCountryPhoneOption } from "$lib/formatting/location";
  import type { CountryModel } from "$lib/models/location";
  import Collapsible from "../../collapsible.svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import countryData from "~/data/country-data";
  import { getTranslator } from "$lib/i18n";
  import { findCountry, getPhoneNumber } from "$lib/utils/country";

  export let data: MobileSchemas.ContactDetails;
  export let errors: z.ZodFormattedError<MobileSchemas.ContactDetails> | undefined = undefined;

  const t = getTranslator();

  let collapsible: Collapsible | undefined;
  let country: CountryModel | undefined = countryData.mapping[data.address.countryCode ?? ""];

  let phone: {
    country?: CountryModel;
    number: string;
  } = getPhoneNumber(data.phone);

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

<Collapsible bind:this={collapsible} title={$t("words.contactInformation")} expandedOnMount>
  <div class="details">
    <div class="phone">
      <SelectField
        search={findCountry}
        options={countryData.list}
        label={$t("words.countryCode")}
        placeholder={$t("actions.select")}
        required
        formatter={formatCountryPhoneOption.bind(formatCountryPhoneOption, $t)}
        bind:value={phone.country}
        error={Boolean(errors?.phone?._errors)}
        dialogMinWidth="240px"
      />
      <TextField
        label={$t("words.phoneNumber")}
        type="tel"
        placeholder={$t("actions.enterPhoneNumber")}
        required
        bind:value={phone.number}
        error={errors?.phone?._errors}
      />
    </div>

    <TextField
      label={$t("words.email")}
      type="email"
      placeholder={$t("actions.enterEmail")}
      required
      bind:value={data.email}
      error={errors?.email?._errors}
    />
    <TextField
      label={$t("words.addressLine1")}
      placeholder={$t("actions.enterAddressLine1")}
      required
      bind:value={data.address.street.line1}
      error={errors?.address?.street?.line1?._errors}
    />
    <TextField
      label={$t("words.addressLine2")}
      placeholder={$t("actions.enterAddressLine2")}
      bind:value={data.address.street.line2}
      error={errors?.address?.street?.line2?._errors}
    />

    <div class="location">
      <TextField
        label={$t("words.city")}
        placeholder="{$t('actions.enterCity')},"
        required
        bind:value={data.address.city}
        error={errors?.address?.city?._errors}
      />
      <SelectField
        search={findCountry}
        direction="up"
        options={countryData.list}
        label={$t("words.country")}
        placeholder={$t("actions.selectCountry")}
        formatter={formatCountryOption.bind(formatCountryOption, $t)}
        required
        bind:value={country}
        error={errors?.address?.countryCode?._errors}
        dialogMinWidth="240px"
      />
      <TextField
        label={$t("words.postcode")}
        placeholder={$t("actions.enterPostcode")}
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
