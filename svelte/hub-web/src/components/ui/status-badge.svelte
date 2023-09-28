<script lang="ts" context="module">
  import type { BookingStatus } from "integration/junction-mobile-api/schemas/booking";
  import type { ConversionStatus } from "integration/junction-hub-api/schemas/conversion";
  import type { TransactionStatus } from "integration/junction-hub-api/schemas/transaction";

  export type StatusBadgeVariant = "ok" | "warn" | "error";
  export type StatusBadgeValue =
    | BookingStatus
    | ConversionStatus
    | TransactionStatus
    | "completed"
    | "deleted"
    | "unknown";

  const statusMapping: Record<StatusBadgeValue, StatusBadgeVariant> = {
    confirmed: "ok",
    completed: "ok",
    executed: "ok",
    paid: "ok",
    error: "error",
    rejected: "error",
    deleted: "error",
    failed: "error",
    pending: "warn",
    "not-ticketed": "warn",
    cancelled: "warn",
    unspecified: "warn",
    unknown: "warn",
  };
</script>

<script lang="ts">
  import { capitalize } from "utils/common";

  export let value: StatusBadgeValue;

  $: variant = statusMapping[value] ?? "ok";
</script>

<span
  class="status-badge typography body-small"
  class:ok={variant === "ok"}
  class:warn={variant === "warn"}
  class:error={variant === "error"}
>
  {capitalize(value).replaceAll("-", " ")}
</span>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 8px;
    color: var(--color-common-dark-strong);
    color: var(--color-main-neutral-900);
    border: 1px solid #d8dadd;
    border-radius: 4px;
  }

  .ok {
    color: var(--color-semantic-success-600);
    background-color: var(--color-semantic-success-50);
    border-color: var(--color-semantic-success-200);
  }

  .error {
    color: var(--color-semantic-error-600);
    background-color: var(--color-semantic-error-100);
    border-color: var(--color-semantic-error-200);
  }

  .warn {
    color: var(--color-semantic-warning-600);
    background-color: var(--color-semantic-warning-50);
    border-color: var(--color-semantic-warning-200);
  }
</style>
