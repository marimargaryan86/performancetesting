<script lang="ts" context="module">
  export type PassengerData = {
    title?: PassengerTitle;
    firstName?: string;
    lastName?: string;
    dateOfBirth?: Date;
    gender?: PassengerGender;
    type: "adult" | "child" | "infant";
    document: PassengerDocument;
  };

  type PassportDocument = {
    type: "passport";
    number?: string;
  };

  type PassengerDocument = PassportDocument | { type?: undefined };

  const travelerDocumentTypes = ["passport"] as const;
  type TravelerDocumentType = (typeof travelerDocumentTypes)[number];

  const passengerGenders = ["unspecified", "male", "female"] as const;
  type PassengerGender = (typeof passengerGenders)[number];

  const passengerTitles = ["unspecified", "mr", "mrs", "ms", "miss"] as const;
  type PassengerTitle = (typeof passengerTitles)[number];

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
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { capitalize } from "utils/common";

  export let passengers: PassengerData[];
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
        />

        <span />

        <TextField
          bind:value={passenger.firstName}
          placeholder="Enter first name"
          label="First name"
          required
        />

        <TextField
          bind:value={passenger.lastName}
          placeholder="Enter last name"
          label="Last name"
          required
        />

        <TextField
          type="date"
          bind:value={passenger.dateOfBirth}
          placeholder="dd/mm/yyyy"
          label="Birthday"
          required
        />

        <SelectField
          options={passengerGenders}
          formatter={formatGenderOption}
          bind:value={passenger.gender}
          placeholder="Select"
          label="Gender"
          required
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
