<script lang="ts" context="module">
  export type FilterOptions = {
    departureAtRange?: DateRange;
    createdAtRange?: DateRange;
    bookingStatus?: BookingStatus;
  };

  export type FilterOptionsQuery = {
    "departureAt[from]"?: string;
    "departureAt[to]"?: string;
    "createdAt[from]"?: string;
    "createdAt[to]"?: string;
    bookingStatus?: string;
  };

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
  import Button from "components/ui/button.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import { getLocaleData, type LocaleData } from "i18n";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import type { DateRange } from "models/date-time";

  export let filters: FilterOptions;

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

<Button class="filter-clear-btn" size="small" on:click={reset}>{$i18n.actions.clear}</Button>

<style>
  :global(button.filter-clear-btn.filter-clear-btn) {
    align-self: flex-end;
    width: unset;
  }
</style>
