<script lang="ts">
  import type { ConversionStatus } from "models/conversion";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import { formatConversionStatus } from "formatting/conversion";

  export let value: ConversionStatus;

  const variants: { unspecified: string; executed: string; failed: string } = {
    executed: "ok",
    unspecified: "warn",
    failed: "error",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={formatConversionStatus(value)} />
