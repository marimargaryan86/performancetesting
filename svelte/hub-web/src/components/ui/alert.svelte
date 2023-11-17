<script lang="ts" context="module">
  export type AlertType = "success" | "error" | "warning";
</script>

<script lang="ts">
  import CloseIcon from "components/icons/close-icon.svelte";
  import { slideFade } from "transitions/slide-fade";

  export let type: AlertType = "success";
  export let show = true;
  let className: string | undefined = undefined;
  export { className as class };
  export let dismissable = true;

  function close(): void {
    show = false;
  }
</script>

{#if show || !dismissable}
  <div
    class={className}
    class:alert={true}
    class:success={type === "success"}
    class:warning={type === "warning"}
    class:error={type === "error"}
    transition:slideFade={{ duration: 300 }}
  >
    <div class="content">
      <slot />
    </div>

    {#if dismissable}
      <button on:click={close}>
        <CloseIcon variant="cross" />
      </button>
    {/if}
  </div>
{/if}

<style>
  .alert {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border: 1px solid transparent;
    border-radius: 16px;
    transition:
      border-color 200ms ease,
      background-color 200ms ease;
  }

  .alert.success {
    background-color: var(--color-semantic-success-100);
    border-color: var(--color-semantic-success-600);
  }

  .alert.error {
    background-color: var(--color-semantic-error-100);
    border-color: var(--color-semantic-error-600);
  }

  .alert.warning {
    background-color: var(--color-semantic-warning-100);
    border-color: var(--color-semantic-warning-600);
  }

  .content {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .content > :global(*) {
    flex-shrink: 0;
  }

  button {
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  button > :global(svg) {
    vertical-align: top;
  }
</style>
