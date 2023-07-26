<script lang="ts">
  import RemoveIcon from "components/icons/remove-icon.svelte";

  export let value: string | null = null;
  export let direction: string;
  export let firstStep = false;

  function handleChange(event): void {
    value = event.target.value;
  }

  function clearValue(): void {
    value = null;
  }
</script>

<div class="input-wrapper">
  <label for={direction} class={firstStep ? "" : "typography body-small"}
    >{direction} <span class="required-fields">{firstStep ? "*" : ""}</span></label
  >
  <input
    id={direction}
    class={firstStep ? "first-step-input" : ""}
    type="text"
    placeholder="City or Station"
    {value}
    on:input={handleChange}
  />
  {#if value}
    <button
      type="button"
      on:click|stopPropagation={clearValue}
      class="clear {firstStep ? '' : 'not-first-step-clear'}"
    >
      <RemoveIcon color="var(--color-common-dark-strong)" />
    </button>
  {/if}
</div>

<style>
  .required-fields {
    color: var(--color-main-primary-500);
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

  .input-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-right: 8px;
  }

  .input-wrapper label {
    margin-bottom: 8px;
  }

  .input-wrapper input {
    height: 40px;
    padding: 10px 16px;
    border: 1px solid var(--color-common-line-medium);
    border-radius: 8px;
  }

  .input-wrapper .first-step-input {
    height: 52px;
    padding: 13px 16px;
    border: 1px solid var(--color-common-line-medium);
    border-radius: 8px;
  }
</style>
