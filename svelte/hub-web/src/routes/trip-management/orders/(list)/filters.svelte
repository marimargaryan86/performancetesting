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

  function formatBookingStatusOptions(
    bookingStatus: BookingStatus | undefined,
    selected = false,
  ): string | undefined {
    if (selected && !bookingStatus) {
      return undefined;
    }

    return bookingStatus ? capitalize(bookingStatus).replaceAll("-", " ") : "None";
  }
</script>

<script lang="ts">
  import Button from "components/ui/button.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import {
    bookingStatuses,
    type BookingStatus,
  } from "integration/junction-hub-api/schemas/booking";
  import type { DateRange } from "models/date-time";
  import { capitalize } from "utils/common";

  export let filters: FilterOptions;

  function reset(): void {
    filters = {};
  }
</script>

<DatePicker
  bind:value={filters.departureAtRange}
  label="Departure date"
  range
  placeholder="Date Range"
/>

<DatePicker
  bind:value={filters.createdAtRange}
  label="Created date"
  range
  placeholder="Date Range"
/>

<SelectField
  label="Booking status"
  bind:value={filters.bookingStatus}
  options={[undefined, ...bookingStatuses]}
  formatter={formatBookingStatusOptions}
  placeholder="Select"
/>

<Button class="filter-clear-btn" size="small" on:click={reset}>Clear</Button>

<style>
  :global(.select-field) {
    --options-z-index: 21;
  }

  :global(button.filter-clear-btn.filter-clear-btn) {
    align-self: flex-end;
    width: unset;
  }
</style>
