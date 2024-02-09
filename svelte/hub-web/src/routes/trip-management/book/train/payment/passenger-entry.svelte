<script lang="ts" context="module">
  const passengerGenders: Gender[] = ["unspecified", "male", "female"];
  const travelerDocumentTypes: TravelerDocumentType[] = ["passport"];

  export type PartialPassengerData = Omit<Partial<OrderPassenger>, "document"> & {
    type: keyof PassengerPickerData;
    document?: Require<Partial<TravelerDocument>, "countryCodes">;
  };

  function formatTitleOption(translator: Translator, option?: PassengerTitle): string {
    return option ? translator(`passengerTitle.${option}`) : "";
  }

  function formatGenderOption(translator: Translator, option?: Gender): string {
    return option ? translator(`gender.${option}`) : "";
  }

  function formatTravelerDocumentOption(
    translator: Translator,
    option?: TravelerDocumentType,
  ): string {
    return option ? translator(`documentTypes.${option}`) : translator("words.none");
  }

  function getPassengerTitles(locale: Locale): PassengerTitle[] {
    const base: PassengerTitle[] = ["unspecified", "mr", "mrs", "miss"];

    if (locale === "es-ES" || locale === "sv") {
      return base;
    }

    // Only add ms for English locale
    return [...base, "ms"];
  }
</script>

<script lang="ts">
  import type { z } from "zod";
  import DateTextField from "~/components/ui/date-text-field.svelte";
  import SelectField from "~/components/ui/select-field.svelte";
  import TextField from "~/components/ui/text-field.svelte";
  import type {
    OrderPassenger,
    TravelerDocument,
  } from "~/integration/junction-mobile-api/schemas/order";
  import Collapsible from "../../../components/collapsible.svelte";
  import type { TripOfferPriceQuote } from "~/integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import type { Require } from "~/integration/ts-helpers";
  import {
    getPassengerFullLabel,
    PASSENGER_DEFINITIONS,
    type PassengerPickerData,
  } from "../../../components/trip-search/passenger-picker/passenger-picker.svelte";
  import { getLocale, getTranslator, type Locale, type Translator } from "~/i18n";
  import type {
    Gender,
    TravelerDocumentType,
    PassengerTitle,
  } from "~/integration/common/schemas/order";

  export let passengerNumber: number;
  export let passenger: PartialPassengerData;
  export let errors: z.ZodFormattedError<OrderPassenger> | undefined = undefined;
  export let required: TripOfferPriceQuote["required"];

  const locale = getLocale();
  const t = getTranslator();

  let collapsible: Collapsible | undefined;
  let document = passenger.document ?? { countryCodes: {} };

  $: passenger = { ...passenger, document };
  $: if (errors) {
    collapsible?.open();
  }
</script>

<Collapsible expandedOnMount bind:this={collapsible}>
  <h2 slot="title">
    <strong typography="title-medium" weight="bold">
      {$t("words.passenger_one")}
      {passengerNumber}
    </strong>
    <span typography="title-small">
      {getPassengerFullLabel(PASSENGER_DEFINITIONS[passenger.type], $t)}
    </span>
  </h2>

  <div class="details">
    <SelectField
      options={getPassengerTitles($locale)}
      formatter={formatTitleOption.bind(formatTitleOption, $t)}
      bind:value={passenger.title}
      placeholder={$t("actions.select")}
      label={$t("words.title")}
      required
      error={errors?.title?._errors}
    />

    <span />

    <TextField
      bind:value={passenger.firstName}
      placeholder={$t("actions.enterFirstName")}
      label={$t("words.firstName")}
      required
      error={errors?.firstName?._errors}
    />

    <TextField
      bind:value={passenger.lastName}
      placeholder={$t("actions.enterLastName")}
      label={$t("words.lastName")}
      required
      error={errors?.lastName?._errors}
    />

    <DateTextField
      bind:value={passenger.birthDate}
      placeholder="dd/mm/yyyy"
      label={$t("words.birthdayDate")}
      required
      error={errors?.birthDate?._errors}
    />

    <SelectField
      options={passengerGenders}
      formatter={formatGenderOption.bind(formatGenderOption, $t)}
      bind:value={passenger.gender}
      placeholder={$t("actions.select")}
      label={$t("words.gender")}
      required
      error={errors?.gender?._errors}
    />

    {#if required.length}
      <SelectField
        bind:value={document.type}
        options={[undefined, ...travelerDocumentTypes]}
        formatter={formatTravelerDocumentOption.bind(formatTravelerDocumentOption, $t)}
        placeholder={$t("actions.select")}
        label={$t("words.documentType")}
        required
        error={errors?.document?.type?._errors}
      />
    {/if}

    {#if document.type === "passport"}
      {#if required.includes("passport-number")}
        <TextField
          bind:value={document.number}
          placeholder={$t("actions.enterDocumentNumber")}
          label={$t("words.documentNumber")}
          required
          error={errors?.document?.number?._errors}
        />
      {/if}
      {#if required.includes("expiration-date")}
        <DateTextField
          bind:value={document.expiryDate}
          placeholder="dd/mm/yyyy"
          label={$t("words.expiryDate")}
          required
          error={errors?.document?.expiryDate?._errors}
        />
      {/if}
      {#if required.includes("issue-date")}
        <DateTextField
          bind:value={document.issueDate}
          placeholder="dd/mm/yyyy"
          label={$t("words.issueDate")}
          required
          error={errors?.document?.issueDate?._errors}
        />
      {/if}
      {#if required.includes("issuing-country")}
        <TextField
          bind:value={document.countryCodes.issue}
          placeholder={$t("actions.enterIssuingCountry")}
          label={$t("words.issuingCountry")}
          required
          error={errors?.document?.countryCodes?.issue?._errors}
        />
      {/if}
      {#if required.includes("nationality")}
        <TextField
          bind:value={document.countryCodes.nationality}
          placeholder={$t("actions.enterNationality")}
          label={$t("words.nationality")}
          required
          error={errors?.document?.countryCodes?.nationality?._errors}
        />
      {/if}
      {#if required.includes("residence-country-code")}
        <TextField
          bind:value={document.countryCodes.residence}
          placeholder={$t("actions.enterResidenceCountryCode")}
          label={$t("words.residenceCountryCode")}
          required
          error={errors?.document?.countryCodes?.residence?._errors}
        />
      {/if}
    {/if}
  </div>
</Collapsible>

<style>
  h2 {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .details {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px 24px;
  }

  .details :global(.select-field),
  .details :global(.text-field) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
    --height: 40px;
  }
</style>
