<script lang="ts">
  import type { ConversionStatus } from "integration/junction-pay/schemas/conversion";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import { capitalize } from "utils/common";

  export let value: ConversionStatus;

  const variants: {
    unspecified: StatusBadgeVariant;
    executed: StatusBadgeVariant;
    failed: StatusBadgeVariant;
  } = {
    executed: "ok",
    unspecified: "warn",
    failed: "error",
  };

  let variant: StatusBadgeVariant = variants[value];

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={capitalize(value)} />
