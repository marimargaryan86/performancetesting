<script lang="ts">
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";
  import type { TransactionStatus } from "integration/junction-pay/schemas/transaction";
  import { capitalize } from "utils/common";

  export let value: TransactionStatus;

  const variants: Record<TransactionStatus, StatusBadgeVariant> = {
    paid: "ok",
    pending: "warn",
    cancelled: "error",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={capitalize(value)} />
