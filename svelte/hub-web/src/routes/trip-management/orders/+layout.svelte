<script lang="ts" context="module">
  import type { Tab } from "components/ui/tabs.svelte";

  type ViewId = "all" | "cancellations" | "refunds";

  const tabs: Record<ViewId, Tab> = {
    all: { url: routeConfig.routes.tripManagement.routes.orders.root, label: "All", exact: true },
    cancellations: {
      url: routeConfig.routes.tripManagement.routes.orders.routes.cancellations.root,
      label: "Cancellations",
      exact: true,
    },
    refunds: {
      url: routeConfig.routes.tripManagement.routes.orders.routes.refunds.root,
      label: "Refunds",
      exact: true,
    },
  };

  export const departureAtDateRange = writable<DateRange | undefined>(undefined);
  export const createdAtDateRange = writable<DateRange | undefined>(undefined);
  export const searchQuery = writable("");
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import routeConfig from "routeConfig";
  import { writable } from "svelte/store";
  import type { DateRange } from "models/date-time";
  import Button from "components/ui/button.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
</script>

<StandardLayout pageTitle="Orders" tabs={Object.values(tabs)} bind:searchQuery={$searchQuery}>
  <Button size="small" href={routeConfig.routes.tripManagement.routes.book.root} slot="actions">
    New Order
    <PlusIcon />
  </Button>

  <svelte:fragment slot="filters">
    <DatePicker
      bind:value={$departureAtDateRange}
      label="Departure date"
      range
      placeholder="Date Range"
    />
    <DatePicker
      bind:value={$createdAtDateRange}
      label="Created date"
      range
      placeholder="Date Range"
    />
  </svelte:fragment>

  <slot />
</StandardLayout>
