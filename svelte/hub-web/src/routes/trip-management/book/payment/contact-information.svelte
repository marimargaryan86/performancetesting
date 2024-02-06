<script lang="ts" context="module">
  export const contactDetailsModel: z.ZodType<ContactDetails> = z.object({
    email: z.string().email().trim(),
    address: z.object({
      street: z.object({
        line1: z.string().trim().min(1),
        line2: z
          .union([z.string().trim().length(0), z.string().trim().min(1)])
          .optional()
          .transform((val) => (val?.length ? val : undefined)),
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

  function getPhoneNumber(phone: string): { country?: CountryModel; number: string } {
    const formattedPhone = phone.replaceAll(/[+\s]/g, "");
    const country = countryData.list.find((item) => formattedPhone.startsWith(item.phoneCode));
    const number = country ? formattedPhone.slice(country.phoneCode.length) : phone;

    return { country, number };
  }
</script>

<script lang="ts">
  import { z } from "zod";
  import SelectField from "~/components/ui/select-field.svelte";
  import TextField from "~/components/ui/text-field.svelte";
  import { formatCountryOption, formatCountryPhoneOption } from "~/formatting/location";
  import type { CountryModel } from "~/models/location";
  import Collapsible from "../../components/collapsible.svelte";
  import type { ContactDetails } from "~/integration/junction-mobile-api/schemas/journey";
  import countryData from "~/data/country-data";
  import { getTranslator } from "~/i18n";

  export let data: ContactDetails;
  export let errors: z.ZodFormattedError<ContactDetails> | undefined = undefined;

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
