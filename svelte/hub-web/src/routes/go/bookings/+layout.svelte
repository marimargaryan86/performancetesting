<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import { conversionStatus } from "models/conversion";
  import { formatConversionStatus } from "formatting/conversion";
  import StandardLayout from "components/page/standard-layout.svelte";
</script>

<StandardLayout pageTitle="Bookings" searchQuery="">
  <svelte:fragment slot="filters">
    <DatePicker range placeholder="Date Range" />
    <StatusPicker
      statuses={conversionStatus}
      format={formatConversionStatus}
      placeholder="Status"
    />
  </svelte:fragment>

  <slot />
</StandardLayout>
