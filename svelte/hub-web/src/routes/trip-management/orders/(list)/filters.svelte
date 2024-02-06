<script lang="ts" context="module">
  function getBookingStatusOptionFormatter(
    translator: Translator,
  ): (status?: BookingStatus, selected?: boolean) => string | undefined {
    return (status, selected) => {
      if (!status) {
        return selected ? undefined : translator("words.none");
      }

      return translator(`statuses.${status}`);
    };
  }
</script>

<script lang="ts">
  import DatePicker from "~/components/ui/date-picker/date-picker.svelte";
  import SelectField from "~/components/ui/select-field.svelte";
  import TextField from "~/components/ui/text-field.svelte";
  import { getTranslator, type Translator } from "~/i18n";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "~/integration/junction-hub-api/schemas/booking";
  import type { JourneyFilterOptions } from "~/integration/junction-hub-api/schemas/journey";
  import { queryFiltersValid } from "./+page.svelte";

  export let filters: JourneyFilterOptions;

  let departureAtFrom: Date | undefined = filters.departureAtRange?.from;
  let createdAtFrom: Date | undefined = filters.createdAtRange?.from;

  // TODO: Update once date picker range is implemented
  $: filters.departureAtRange = departureAtFrom
    ? {
        from: departureAtFrom,
        to: new Date(
          departureAtFrom.getFullYear(),
          departureAtFrom.getMonth(),
          departureAtFrom.getDate() + 5,
        ),
      }
    : undefined;
  $: filters.createdAtRange = createdAtFrom
    ? {
        from: createdAtFrom,
        to: new Date(
          createdAtFrom.getFullYear(),
          createdAtFrom.getMonth(),
          createdAtFrom.getDate() + 5,
        ),
      }
    : undefined;
  $: if (filters.passengerLastName?.length === 0) {
    filters.passengerLastName = undefined;
  }
  $: if (filters.passengerNameRecord?.length === 0) {
    filters.passengerNameRecord = undefined;
  }

  $: valid = queryFiltersValid(filters);
  $: errors = {
    passengerNameRecord:
      valid.passengerNameRecord === false ? $t("sentences.passengerNameRecordError") : false,
  };

  const t = getTranslator();

  function reset(): void {
    departureAtFrom = undefined;
    createdAtFrom = undefined;
    filters = {};
  }
</script>

<DatePicker bind:value={departureAtFrom} label={$t("tableHeaders.departureDate")} />

<DatePicker bind:value={createdAtFrom} label={$t("tableHeaders.createdDate")} />

<SelectField
  label={$t("tableHeaders.bookingStatus")}
  bind:value={filters.bookingStatus}
  options={[undefined, ...bookingStatuses]}
  formatter={getBookingStatusOptionFormatter($t)}
  placeholder={$t("actions.select")}
/>

<TextField
  label={$t("words.passengerNameRecord")}
  placeholder={$t("sentences.passengerNameRecordPlaceholder")}
  bind:value={filters.passengerNameRecord}
  error={errors.passengerNameRecord}
/>

<TextField
  label={`${$t("words.passenger_one")} ${$t("words.lastName").toLowerCase()} (${$t(
    "words.optional",
  ).toLowerCase()})`}
  placeholder={$t("sentences.passengerLastNamePlaceholder")}
  bind:value={filters.passengerLastName}
/>

<button class="clear" variant="primary" size="small" on:click={reset}>
  {$t("actions.clearAll")}
</button>

<style>
  .clear {
    width: unset;
    min-width: 80px;
  }
</style>
