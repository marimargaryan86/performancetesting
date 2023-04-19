<script lang="ts">
  import type { ConversionStatus } from "models/conversion";
  import StatusBadge from "./status-badge.svelte";
  import { formatConversionStatus } from "formatting/conversion";

  export let value: ConversionStatus;

  $: variant = {
    executed: 0,
    unspecified: 1,
  }[value];
</script>

<StatusBadge {variant} value={formatConversionStatus(value)} />
