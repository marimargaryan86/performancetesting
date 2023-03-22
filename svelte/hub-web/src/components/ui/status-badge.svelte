<script lang="ts">
  export let value: string;
  export let variant: number;
</script>

<span
  class="status-badge"
  class:ok={variant === 0}
  class:warn={variant === 1}
  class:error={variant === 2}
>
  {value}
</span>

<style>
  .status-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    color: var(--color-generic-white);
    color: var(--color-neutral-900);
    font-weight: 600;
    font-size: 8px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 12px;
    letter-spacing: 0.15px;
    border: 1px solid #d8dadd;
    border-radius: 8px;
  }

  .ok {
    border-color: var(--color-success-500);
  }

  .error {
    border-color: var(--color-error-500);
  }

  .warn {
    border-color: var(--color-warning-500);
  }
</style>
