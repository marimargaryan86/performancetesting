<script lang="ts">
  import { formatTransactionStatus } from "formatting/transaction";
  import type { TransactionStatus } from "models/transaction";
  import StatusBadge from "./status-badge.svelte";

  export let value: TransactionStatus;

  $: variant = {
    paid: 0,
    pending: 1,
    cancelled: 2,
  }[value];
</script>

<StatusBadge {variant} value={formatTransactionStatus(value)} />
