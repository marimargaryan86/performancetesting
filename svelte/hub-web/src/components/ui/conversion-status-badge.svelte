<script lang="ts">
  import type { ConversionStatus } from "models/conversion";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import { formatConversionStatus } from "formatting/conversion";

  export let value: ConversionStatus;

  const variants: Record<ConversionStatus, StatusBadgeVariant> = {
    executed: "ok",
    unspecified: "warn",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={formatConversionStatus(value)} />
