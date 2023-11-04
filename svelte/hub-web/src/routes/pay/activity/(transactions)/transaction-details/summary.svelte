<script lang="ts">
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import StatusBadge, { type StatusBadgeValue } from "components/ui/status-badge.svelte";
  import { yymmdd } from "formatting/date-time";
  import type { TripBooking } from "integration/junction-hub-api/schemas/booking";
  import type { Transaction } from "integration/junction-hub-api/schemas/transaction";

  export let booking: TripBooking;
  export let transaction: Transaction;

  $: status = booking.status as StatusBadgeValue;
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
      <StatusBadge value={status} />
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
