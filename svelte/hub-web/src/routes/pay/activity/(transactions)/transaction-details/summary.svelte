<script lang="ts">
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import StatusBadge from "components/ui/status-badge.svelte";
  import { yymmdd } from "formatting/date-time";
</script>

<div class="summary">
  <h3 class="typography title-medium bold">Summary</h3>

  <div class="item">
    <strong class="typography body-small">Vendor</strong>
    <span class="typography body-medium company">
      <EntityAvatar name="Air France" />
      Air France
    </span>
  </div>

  <div class="item">
    <strong class="typography body-small">Status</strong>
    <span class="typography body-medium">
      <StatusBadge value="Paid" />
    </span>
  </div>

  <div class="item">
    <strong class="typography body-small">Reference</strong>
    <span class="typography body-medium bold">HZEMS</span>
  </div>

  <div class="item">
    <strong class="typography body-small">Issued</strong>
    <span class="typography body-medium bold">{yymmdd(new Date())}</span>
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
