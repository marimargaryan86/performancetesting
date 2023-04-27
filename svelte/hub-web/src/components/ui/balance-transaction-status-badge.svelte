<script lang="ts">
  import { formatBalanceTransactionStatus } from "formatting/transaction";
  import type { BalanceTransactionStatus } from "models/transaction";
  import StatusBadge, { type StatusBadgeVariant } from "./status-badge.svelte";

  export let value: BalanceTransactionStatus;

  const variants: Record<BalanceTransactionStatus, StatusBadgeVariant> = {
    completed: "ok",
    pending: "warn",
    deleted: "error",
  };

  $: variant = variants[value];
</script>

<StatusBadge {variant} value={formatBalanceTransactionStatus(value)} />
