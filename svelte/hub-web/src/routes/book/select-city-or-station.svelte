<script lang="ts">
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import TextField from "components/ui/text-field.svelte";

  export let value: string | undefined = undefined;
  export let direction: string;
  export let firstStep = false;

  function clearValue(): void {
    value = undefined;
  }
</script>

<div class="input-wrapper">
  <TextField
    label={direction}
    required={firstStep}
    id={direction}
    placeholder="City or Station"
    bind:value
  />

  {#if value}
    <button
      type="button"
      on:click={clearValue}
      class="clear"
      class:not-first-step-clear={!firstStep}
    >
      <RemoveIcon color="var(--color-common-dark-strong)" />
    </button>
  {/if}
</div>

<style>
  .input-wrapper {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    margin-right: 8px;
  }

  .input-wrapper > :global(.text-field) {
    --x-label-font-size: 16px;
  }

  .clear {
    position: absolute;
    top: 58%;
    right: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    padding: 8px 2px;
    background: var(--color-main-neutral-400);
    border: 0;
    border-radius: 50%;
    cursor: pointer;
  }

  .clear.not-first-step-clear {
    top: 53%;
  }
</style>
