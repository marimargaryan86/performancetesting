<script lang="ts">
  import type { z } from "zod";
  import DateTextField from "$lib/components/ui/date-text-field.svelte";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import Collapsible from "../../collapsible.svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { getLocale, getTranslator } from "$lib/i18n";
  import {
    formatTitleOption,
    getPassengerTitles,
    PASSENGER_GENDERS,
    type PartialPassengerData,
    formatGenderOption,
    TRAVELER_DOCUMENT_TYPES,
    formatTravelerDocumentOption,
  } from "$lib/models/passenger";

  export let passengerNumber: number;
  export let passenger: PartialPassengerData;
  export let errors: z.ZodFormattedError<MobileSchemas.OrderPassenger> | undefined = undefined;
  export let required: MobileSchemas.TripOfferPriceQuote["required"];

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
      {$t(`passengerTypes.${passenger.type}`, { count: 1 })}

      {#if passenger.type !== "adult"}
        ({$t("words.year", { count: passenger.age })})
      {/if}
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
      options={PASSENGER_GENDERS}
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
        options={[undefined, ...TRAVELER_DOCUMENT_TYPES]}
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
