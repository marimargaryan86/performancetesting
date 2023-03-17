<script lang="ts">
  import { formatBalanceTransactionStatus } from "formatting/transaction";
  import type { BalanceTransactionStatus } from "models/transaction";
  import StatusBadge from "./status-badge.svelte";

  export let value: BalanceTransactionStatus;

  $: variant = {
    completed: 0,
    pending: 1,
    deleted: 2,
  }[value];
</script>

<StatusBadge {variant} value={formatBalanceTransactionStatus(value)} />
