<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import { STATUS_BADGE_MAPPING, type StatusBadgeValue } from "$lib/models/status-badge";

  export let value: StatusBadgeValue;

  const t = getTranslator();

  $: variant = STATUS_BADGE_MAPPING[value];
</script>

<span
  typography="body-small"
  class="status-badge"
  class:ok={variant === "ok"}
  class:warn={variant === "warn"}
  class:error={variant === "error"}
>
  {$t(`statuses.${value}`)}
</span>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 8px;
    color: var(--color-common-dark-strong);
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
