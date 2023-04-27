<script lang="ts">
  import { formatTransactionStatus } from "formatting/transaction";
  import type { TransactionStatus } from "models/transaction";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";

  export let value: TransactionStatus;

  const variants: Record<TransactionStatus, StatusBadgeVariant> = {
    paid: "ok",
    pending: "warn",
    cancelled: "error",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={formatTransactionStatus(value)} />
