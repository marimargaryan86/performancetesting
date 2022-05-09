<script lang="ts">
  type T = $$Generic<string | number>;

  export let max: number = undefined;
  export let min: number = undefined;
  export let type: "number" | "text" = "text";
  export let value: T = undefined;
  export let label: string = undefined;
  export let placeholder: string = undefined;
  export let readonly = false;
  export let tabindex: 0 | -1 = undefined;

  let focused = false;

  $: hasValue = focused || (value?.toString().length ?? 0) || (placeholder?.length ?? 0) > 0;
</script>

<div class="text-input" class:has-value={hasValue}>
  {#if type === "number"}
    <label>
      <input
        type="number"
        bind:value
        {placeholder}
        step="any"
        {max}
        {min}
        on:focus={() => (focused = !readonly)}
        on:blur={() => (focused = false)}
        on:change
        on:input
        {readonly}
        {tabindex}
      />

      {#if !!label}<span>{label}</span>{/if}
    </label>
  {:else}
    <label>
      <input
        type="text"
        bind:value
        {placeholder}
        on:focus={() => (focused = !readonly)}
        on:blur={() => (focused = false)}
        on:change
        on:input
        {readonly}
        {tabindex}
      />

      {#if !!label}<span>{label}</span>{/if}
    </label>
  {/if}
</div>

<style>
  .text-input {
    position: relative;
    display: inline-block;
    border-radius: 4px;
    height: 48px;
    border: 1px solid var(--color-gray);
    color: var(--color-black);
    font-size: 14px;
    font-family: "Open Sans", Arial, Helvetica, sans-serif;
    background-color: var(--color-white);
  }

  .text-input:focus-within {
    box-shadow: var(--focus-outline);
  }

  label {
    display: block;
    height: 100%;
    width: 100%;
  }

  span {
    position: absolute;
    display: block;
    font-size: 16px;
    top: 16px;
    left: 8px;
    color: var(--color-teal);
    transition: font-size 150ms ease, top 150ms ease;
    pointer-events: none;
    user-select: none;
  }

  .text-input.has-value span {
    font-size: 12px;
    top: 5.5px;
  }

  input {
    height: 100%;
    width: 100%;
    padding: 8px;
    vertical-align: top;
    font-family: inherit;
    font-size: inherit;
    border: 0;
    background-color: transparent;
    outline: 0;
    margin: 0;
  }

  input::placeholder {
    color: var(--color-gray-dark);
  }

  .text-input.has-value input {
    padding: 14px 8px 0;
  }
</style>
