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
  import { dev } from "$app/environment";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { getLocaleData, type LocaleData } from "i18n";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import type { JourneyFilterOptions } from "integration/junction-hub-api/schemas/journey";

  export let filters: JourneyFilterOptions;

  const i18n = getLocaleData();

  $: formatBookingStatusOption = getBookingStatusOptionFormatter($i18n);

  function reset(): void {
    filters = {};
  }
</script>

<DatePicker
  bind:value={filters.departureAtRange}
  label={$i18n.tableHeaders.departureDate}
  range
  placeholder={$i18n.words.dateRange}
/>

<DatePicker
  bind:value={filters.createdAtRange}
  label={$i18n.tableHeaders.createdDate}
  range
  placeholder={$i18n.words.dateRange}
/>

<SelectField
  label={$i18n.tableHeaders.bookingStatus}
  bind:value={filters.bookingStatus}
  options={[undefined, ...bookingStatuses]}
  formatter={formatBookingStatusOption}
  placeholder={$i18n.actions.select}
/>

{#if dev}
  <TextField
    label={$i18n.words.referenceNumber}
    placeholder={$i18n.sentences.referenceNumberPlaceholder}
    bind:value={filters.referenceNumber}
  />

  <TextField
    label={`${
      $i18n.words.passenger.singular
    } ${$i18n.words.lastName.toLowerCase()} (${$i18n.words.optional.toLowerCase()})`}
    placeholder={$i18n.sentences.passengerLastNamePlaceholder}
    bind:value={filters.passengerLastName}
  />
{/if}

<button class="clear" variant="primary" size="small" on:click={reset}>{$i18n.actions.clear}</button>

<style>
  .clear {
    align-self: flex-end;
    width: unset;
    min-width: 80px;
  }
</style>
