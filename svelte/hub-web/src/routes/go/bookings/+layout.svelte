<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import StatusPicker from "components/ui/status-picker.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import { capitalize } from "utils/common";
</script>

<StandardLayout pageTitle="Bookings" searchQuery="">
  <svelte:fragment slot="filters">
    <DatePicker range placeholder="Date Range" />
    <StatusPicker
      statuses={["executed", "unspecified", "failed"]}
      format={capitalize}
      placeholder="Status"
    />
  </svelte:fragment>

  <slot />
</StandardLayout>
