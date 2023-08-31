<script lang="ts" context="module">
  const passengerTitles = ["unspecified", "mr", "mrs", "ms", "miss"] as const;
  const passengerTitle = z.enum(passengerTitles, { required_error: "Title is required" });
  type PassengerTitle = z.infer<typeof passengerTitle>;

  const passengerGenders = ["unspecified", "male", "female"] as const;
  const passengerGender = z.enum(passengerGenders, { required_error: "Gender is required" });
  type PassengerGender = z.infer<typeof passengerGender>;

  const passportDocument = z.object({
    type: z.literal("passport"),
    number: z.string({ required_error: "Passport number required" }),
  });

  const passengerDocument = passportDocument.or(
    z.object({ type: z.undefined().optional(), number: z.string().optional() }),
  );

  export const passengerData = z.object({
    title: passengerTitle,
    firstName: z.string({ required_error: "First name is required" }),
    lastName: z.string({ required_error: "Last name is required" }),
    dateOfBirth: z.date({ required_error: "Date of birth is required" }),
    gender: passengerGender,
    type: z.enum(["adult", "child", "infant"]),
    document: passengerDocument,
  });

  export type PassengerData = z.infer<typeof passengerData>;

  export type PartialPassengerData = PartiallyPartial<PassengerData, "type" | "document">;

  export const passengerListData = z.array(passengerData);
  export type PassengerListData = z.infer<typeof passengerListData>;

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
  import { capitalize, type PartiallyPartial } from "utils/common";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";

  export let passengers: PartialPassengerData[];
  export let errors: z.ZodFormattedError<PassengerListData> | undefined = undefined;
</script>

<div class="passengers">
  {#each passengers as passenger, idx}
    <div class="passenger">
      <h2>
        <strong class="typography title-large bold">Passenger {idx + 1}</strong>
        <span class="typography title-medium">{capitalize(passenger.type)}</span>
      </h2>

      <div class="details">
        <SelectField
          options={passengerTitles}
          formatter={formatTitleOption}
          bind:value={passenger.title}
          placeholder="Select"
          label="Title"
          required
          error={errors?.[idx]?.title?._errors}
        />

        <span />

        <TextField
          bind:value={passenger.firstName}
          placeholder="Enter first name"
          label="First name"
          required
          error={errors?.[idx]?.firstName?._errors}
        />

        <TextField
          bind:value={passenger.lastName}
          placeholder="Enter last name"
          label="Last name"
          required
          error={errors?.[idx]?.lastName?._errors}
        />

        <TextField
          type="date"
          bind:value={passenger.dateOfBirth}
          placeholder="dd/mm/yyyy"
          label="Birthday"
          required
          error={errors?.[idx]?.dateOfBirth?._errors}
        />

        <SelectField
          options={passengerGenders}
          formatter={formatGenderOption}
          bind:value={passenger.gender}
          placeholder="Select"
          label="Gender"
          required
          error={errors?.[idx]?.gender?._errors}
        />

        <SelectField
          options={[undefined, ...travelerDocumentTypes]}
          formatter={formatTravelerDocumentOption}
          bind:value={passenger.document.type}
          placeholder="Select"
          label="Document type"
        />

        {#if passenger.document.type === "passport"}
          <TextField
            bind:value={passenger.document.number}
            placeholder="Enter document number"
            label="Document number"
            required
            error={errors?.[idx]?.document?.number?._errors}
          />
        {/if}
      </div>
    </div>
  {/each}
</div>

<style>
  .passengers {
    display: flex;
    flex-flow: column;
    gap: 24px;
  }

  .passenger {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 40px 80px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  h2 {
    display: flex;
    flex-flow: column;
    gap: 8px;
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
