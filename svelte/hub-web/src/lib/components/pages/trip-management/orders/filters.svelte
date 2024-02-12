<script lang="ts" context="module">
  export function queryFiltersGetter(
    value: HubSchemas.JourneyFilterOptionsQuery,
  ): HubSchemas.JourneyFilterOptions {
    return {
      bookingStatus: HubSchemas.bookingStatuses.find((item) => item === value.bookingStatus),
      createdAtRange: parseDateRange(value["createdAt[from]"], value["createdAt[to]"]),
      departureAtRange: parseDateRange(value["departureAt[from]"], value["departureAt[to]"]),
      passengerLastName:
        value.passengerLastName === undefined || value.passengerLastName.length > 2
          ? value.passengerLastName
          : undefined,
      passengerNameRecord:
        value.passengerNameRecord === undefined ||
        validatePassengerNameRecord(value.passengerNameRecord)
          ? value.passengerNameRecord
          : undefined,
    };
  }
  export function queryFiltersValid(value: HubSchemas.JourneyFilterOptions): {
    [key in keyof HubSchemas.JourneyFilterOptions]?: boolean;
  } {
    return {
      passengerLastName:
        value.passengerLastName === undefined || value.passengerLastName.length > 2,
      passengerNameRecord:
        value.passengerNameRecord === undefined ||
        validatePassengerNameRecord(value.passengerNameRecord),
    };
  }
</script>

<script lang="ts">
  import DatePicker from "$lib/components/ui/date-picker/date-picker.svelte";
  import SelectField from "$lib/components/ui/select-field.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import { getTranslator } from "$lib/i18n";
  import * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import { getBookingStatusOptionFormatter } from "$lib/formatting/booking";
  import { parseDateRange } from "$lib/utils/date-time";
  import { validatePassengerNameRecord } from "$lib/utils/booking";

  export let filters: HubSchemas.JourneyFilterOptions;

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
  options={[undefined, ...HubSchemas.bookingStatuses]}
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
