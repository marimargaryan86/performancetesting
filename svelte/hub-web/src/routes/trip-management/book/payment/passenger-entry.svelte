<script lang="ts" context="module">
  const passengerTitles: OrderPassenger["title"][] = ["unspecified", "mr", "mrs", "ms", "miss"];
  const passengerGenders: OrderPassenger["gender"][] = ["unspecified", "male", "female"];
  const travelerDocumentTypes: NonNullable<TravelerDocument["type"]>[] = ["passport"];

  export type PartialPassengerData = Omit<Partial<OrderPassenger>, "document"> & {
    type: keyof PassengerPickerData;
    document?: Require<Partial<TravelerDocument>, "countryCodes">;
  };

  function formatTitleOption(option?: OrderPassenger["title"]): string {
    return option ? capitalize(option) : "";
  }

  function formatGenderOption(option?: OrderPassenger["gender"]): string {
    return option ? capitalize(option) : "";
  }

  function formatTravelerDocumentOption(option?: NonNullable<TravelerDocument["type"]>): string {
    return option ? capitalize(option) : "None";
  }
</script>

<script lang="ts">
  import type { z } from "zod";
  import { capitalize } from "utils/common";
  import DateTextField from "components/ui/date-text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type {
    OrderPassenger,
    TravelerDocument,
  } from "integration/junction-mobile-api/schemas/order";
  import Collapsible from "../../components/collapsible.svelte";
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";
  import type { Require } from "integration/ts-helpers";
  import {
    getPassengerFullLabel,
    PASSENGER_DEFINITIONS,
    type PassengerPickerData,
  } from "../../components/trip-search/passenger-picker/passenger-picker.svelte";

  export let passengerNumber: number;
  export let passenger: PartialPassengerData;
  export let errors: z.ZodFormattedError<OrderPassenger> | undefined = undefined;
  export let required: TripOfferPriceQuote["required"];

  let collapsible: Collapsible | undefined;
  let document = passenger.document ?? { countryCodes: {} };

  $: passenger = { ...passenger, document };
  $: if (errors) {
    collapsible?.open();
  }
</script>

<Collapsible expandedOnMount bind:this={collapsible}>
  <h2 slot="title">
    <strong class="typography title-medium bold">Passenger {passengerNumber}</strong>
    <span class="typography title-small">
      {getPassengerFullLabel(PASSENGER_DEFINITIONS[passenger.type])}
    </span>
  </h2>

  <div class="details">
    <SelectField
      options={passengerTitles}
      formatter={formatTitleOption}
      bind:value={passenger.title}
      placeholder="Select"
      label="Title"
      required
      error={errors?.title?._errors}
    />

    <span />

    <TextField
      bind:value={passenger.firstName}
      placeholder="Enter first name"
      label="First name"
      required
      error={errors?.firstName?._errors}
    />

    <TextField
      bind:value={passenger.lastName}
      placeholder="Enter last name"
      label="Last name"
      required
      error={errors?.lastName?._errors}
    />

    <DateTextField
      bind:value={passenger.birthDate}
      placeholder="dd/mm/yyyy"
      label="Birthday"
      required
      error={errors?.birthDate?._errors}
    />

    <SelectField
      options={passengerGenders}
      formatter={formatGenderOption}
      bind:value={passenger.gender}
      placeholder="Select"
      label="Gender"
      required
      error={errors?.gender?._errors}
    />

    {#if required.length}
      <SelectField
        options={[undefined, ...travelerDocumentTypes]}
        formatter={formatTravelerDocumentOption}
        bind:value={document.type}
        placeholder="Select"
        label="Document type"
        error={errors?.document?.type?._errors}
      />
    {/if}

    {#if document.type === "passport"}
      {#if required.includes("passport-number")}
        <TextField
          bind:value={document.number}
          placeholder="Enter document number"
          label="Document number"
          required
          error={errors?.document?.number?._errors}
        />
      {/if}
      {#if required.includes("expiration-date")}
        <DateTextField
          bind:value={document.expiryDate}
          placeholder="dd/mm/yyyy"
          label="Expiration date"
          required
          error={errors?.document?.expiryDate?._errors}
        />
      {/if}
      {#if required.includes("issue-date")}
        <DateTextField
          bind:value={document.issueDate}
          placeholder="dd/mm/yyyy"
          label="Issue date"
          required
          error={errors?.document?.issueDate?._errors}
        />
      {/if}
      {#if required.includes("issuing-country")}
        <TextField
          bind:value={document.countryCodes.issue}
          placeholder="Enter issuing country"
          label="Issuing country"
          required
          error={errors?.document?.countryCodes?.issue?._errors}
        />
      {/if}
      {#if required.includes("nationality")}
        <TextField
          bind:value={document.countryCodes.nationality}
          placeholder="Enter nationality"
          label="Nationality"
          required
          error={errors?.document?.countryCodes?.nationality?._errors}
        />
      {/if}
      {#if required.includes("residence-country-code")}
        <TextField
          bind:value={document.countryCodes.residence}
          placeholder="Enter residence country code"
          label="Residence country code"
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
