<script lang="ts">
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import StatusBadge, { type StatusBadgeVariant } from "components/ui/status-badge.svelte";
  import { yymmdd } from "formatting/date-time";
  import type { BookingModel } from "integration/junction-client-api/schemas/booking";
  import type { TransactionModel } from "integration/junction-pay/schemas/transaction";
  import { capitalize } from "utils/common";

  export let booking: BookingModel;
  export let transaction: TransactionModel;

  const statusMapping: Record<string, StatusBadgeVariant> = {
    error: "error",
    "not-ticketed": "warn",
  };
  const labelMapping: Record<string, string> = {
    error: "Error",
    "not-ticketed": "Not ticketed",
  };
</script>

<div class="summary">
  <h3 class="typography title-medium bold">Summary</h3>

  <div class="item">
    <strong class="typography body-small">Vendor</strong>
    <span class="typography body-medium company">
      <EntityAvatar name={transaction.beneficiary?.name} />
      {transaction.beneficiary?.name ?? "N/A"}
    </span>
  </div>

  <div class="item">
    <strong class="typography body-small">Status</strong>
    <span class="typography body-medium">
      <StatusBadge
        value={labelMapping[booking.status] ?? capitalize(booking.status)}
        variant={statusMapping[booking.status] ?? "ok"}
      />
    </span>
  </div>

  <div class="item">
    <strong class="typography body-small">Reference</strong>
    <span class="typography body-medium bold">{booking.externalReference ?? "N/A"}</span>
  </div>

  <div class="item">
    <strong class="typography body-small">Issued</strong>
    <span class="typography body-medium bold">{yymmdd(transaction.createdAt)}</span>
  </div>
</div>

<style>
  .summary {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    padding: 24px;
    color: var(--color-main-neutral-800);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  h3 {
    grid-column: 1 / -1;
    margin-bottom: 8px;
  }

  .item {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  .item > strong {
    color: var(--color-main-neutral-500);
  }

  .item :global(.entity-avatar) {
    flex-shrink: 0;
    box-shadow: 0 0 15px 3px rgb(0 0 0 / 0.04);
  }

  .company {
    display: flex;
    gap: 8px;
    align-items: center;
  }
</style>
