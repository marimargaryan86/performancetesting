<script lang="ts" context="module">
  export type StatusBadgeVariant = "ok" | "warn" | "error";
</script>

<script lang="ts">
  export let value: string;
  export let variant: StatusBadgeVariant = "ok";
</script>

<span
  class="status-badge typography body-small"
  class:ok={variant === "ok"}
  class:warn={variant === "warn"}
  class:error={variant === "error"}
>
  {value}
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
