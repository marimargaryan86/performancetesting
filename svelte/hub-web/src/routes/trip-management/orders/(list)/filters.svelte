<script lang="ts" context="module">
  function getBookingStatusOptionFormatter(
    locale: LocaleData,
  ): (status?: BookingStatus, selected?: boolean) => string | undefined {
    return (status, selected) => {
      if (!status) {
        return selected ? undefined : locale.words.none;
      }

      return locale.statuses[status];
    };
  }
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { getLocaleData, type LocaleData } from "i18n";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import type { JourneyFilterOptions } from "integration/junction-hub-api/schemas/journey";
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
      valid.passengerNameRecord === false ? $i18n.sentences.passengerNameRecordError : false,
  };

  const i18n = getLocaleData();

  function reset(): void {
    departureAtFrom = undefined;
    createdAtFrom = undefined;
    filters = {};
  }
</script>

<DatePicker bind:value={departureAtFrom} label={$i18n.tableHeaders.departureDate} />

<DatePicker bind:value={createdAtFrom} label={$i18n.tableHeaders.createdDate} />

<SelectField
  label={$i18n.tableHeaders.bookingStatus}
  bind:value={filters.bookingStatus}
  options={[undefined, ...bookingStatuses]}
  formatter={getBookingStatusOptionFormatter($i18n)}
  placeholder={$i18n.actions.select}
/>

<TextField
  label={$i18n.words.passengerNameRecord}
  placeholder={$i18n.sentences.passengerNameRecordPlaceholder}
  bind:value={filters.passengerNameRecord}
  error={errors.passengerNameRecord}
/>

<TextField
  label={`${
    $i18n.words.passenger.singular
  } ${$i18n.words.lastName.toLowerCase()} (${$i18n.words.optional.toLowerCase()})`}
  placeholder={$i18n.sentences.passengerLastNamePlaceholder}
  bind:value={filters.passengerLastName}
/>

<button class="clear" variant="primary" size="small" on:click={reset}>
  {$i18n.actions.clearAll}
</button>

<style>
  .clear {
    width: unset;
    min-width: 80px;
  }
</style>
