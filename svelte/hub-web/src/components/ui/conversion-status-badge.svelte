<script lang="ts">
  import type { ConversionStatus } from "models/conversion";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import { formatConversionStatus } from "formatting/conversion";

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

<StatusBadge {variant} value={formatConversionStatus(value)} />
