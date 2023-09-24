<script lang="ts" context="module">
  const passengerTypes = ["adult", "child", "infant"] as const;
  const passengerType = z.enum(passengerTypes);
  type PassengerType = z.infer<typeof passengerType>;

  const passengerTitles = ["unspecified", "mr", "mrs", "ms", "miss"] as const;
  const passengerTitle = z.enum(passengerTitles, { required_error: "Title is required" });
  type PassengerTitle = z.infer<typeof passengerTitle>;

  const passengerGenders = ["unspecified", "male", "female"] as const;
  const passengerGender = z.enum(passengerGenders, { required_error: "Gender is required" });
  type PassengerGender = z.infer<typeof passengerGender>;

  type DocumentValidator = z.ZodObject<{
    [key in keyof PassportDocumentModel]-?: z.ZodType<PassportDocumentModel[key]>;
  }>;

  export type PassengerValidator = z.ZodObject<
    Omit<
      { [key in keyof OrderPassengerModel]: z.ZodType<OrderPassengerModel[key]> },
      "document"
    > & {
      type: typeof passengerType;
      document: DocumentValidator | z.ZodUndefined;
    }
  >;

  export type PartialPassengerData = Omit<Partial<OrderPassengerModel>, "document"> & {
    type: PassengerType;
    document?: Partial<PassportDocumentModel>;
  };

  export function getPassengerValidator(
    required: TripOfferPriceQuoteModel["required"],
  ): PassengerValidator {
    const documentFields: {
      [key in keyof PassportDocumentModel]: z.ZodType<PassportDocumentModel[key]>;
    } = {
      type: z.enum(["passport"]),
    };

    required.forEach((field) => {
      if (field === "expiration-date") {
        documentFields.expirationDate = z.date({ coerce: true });
      } else if (field === "issue-date") {
        documentFields.issueDate = z.date({ coerce: true });
      } else if (field === "issuing-country") {
        documentFields.issueCountry = z.string().nonempty();
      } else if (field === "nationality") {
        documentFields.nationality = z.string().nonempty();
      } else if (field === "passport-number") {
        documentFields.number = z.string().nonempty();
      } else if (field === "residence-country-code") {
        documentFields.residenceCountryCode = z.string().nonempty();
      } else if (field === "date-of-birth") {
        // Date of birth will always be mandatory
      } else {
        throw new Error(`Unhandled field type ${field}`);
      }
    });

    const result = z.object({
      type: passengerType,
      title: passengerTitle,
      firstName: z.string({ required_error: "First name is required" }),
      lastName: z.string({ required_error: "Last name is required" }),
      dateOfBirth: z.date({ coerce: true, required_error: "Date of birth is required" }),
      gender: passengerGender,
    });

    return (Object.keys(documentFields).length > 1
      ? result.extend({ document: z.object({ ...documentFields }) })
      : result) as unknown as PassengerValidator;
  }

  export type PassengerData = z.infer<PassengerValidator>;

  const travelerDocumentTypes = ["passport"] as const;
  type TravelerDocumentType = (typeof travelerDocumentTypes)[number];

  function formatTitleOption(option?: PassengerTitle): string {
    return option ? capitalize(option) : "";
  }

  function formatGenderOption(option?: PassengerGender): string {
    return option ? capitalize(option) : "";
  }

  function formatTravelerDocumentOption(option?: TravelerDocumentType): string {
    return option ? capitalize(option) : "None";
  }
</script>

<script lang="ts">
  import { z } from "zod";
  import { capitalize } from "utils/common";
  import BirthdateTextField from "components/ui/birthdate-text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import type { TripOfferPriceQuoteModel } from "integration/junction-mobile-api/schemas/offer";
  import type {
    OrderPassengerModel,
    PassportDocumentModel,
  } from "integration/junction-mobile-api/schemas/order";

  export let passengerNumber: number;
  export let passenger: PartialPassengerData;
  export let errors: z.ZodFormattedError<PassengerData> | undefined = undefined;
  export let required: TripOfferPriceQuoteModel["required"];

  let document = passenger.document ?? {};

  $: passenger = { ...passenger, document };
</script>

<div class="passenger">
  <h2>
    <strong class="typography title-medium bold">Passenger {passengerNumber}</strong>
    <span class="typography title-small">{capitalize(passenger.type)}</span>
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

    <BirthdateTextField
      bind:value={passenger.dateOfBirth}
      placeholder="dd/mm/yyyy"
      label="Birthday"
      required
      error={errors?.dateOfBirth?._errors}
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
        <TextField
          type="date"
          bind:value={document.expirationDate}
          placeholder="dd/mm/yyyy"
          label="Expiration date"
          required
          error={errors?.document?.expirationDate?._errors}
        />
      {/if}
      {#if required.includes("issue-date")}
        <TextField
          type="date"
          bind:value={document.issueDate}
          placeholder="dd/mm/yyyy"
          label="Issue date"
          required
          error={errors?.document?.issueDate?._errors}
        />
      {/if}
      {#if required.includes("issuing-country")}
        <TextField
          bind:value={document.issueCountry}
          placeholder="Enter issuing country"
          label="Issuing country"
          required
          error={errors?.document?.issueCountry?._errors}
        />
      {/if}
      {#if required.includes("nationality")}
        <TextField
          bind:value={document.nationality}
          placeholder="Enter nationality"
          label="Nationality"
          required
          error={errors?.document?.nationality?._errors}
        />
      {/if}
      {#if required.includes("residence-country-code")}
        <TextField
          bind:value={document.residenceCountryCode}
          placeholder="Enter residence country code"
          label="Residence country code"
          required
          error={errors?.document?.residenceCountryCode?._errors}
        />
      {/if}
    {/if}
  </div>
</div>

<style>
  .passenger {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 24px 40px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

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
