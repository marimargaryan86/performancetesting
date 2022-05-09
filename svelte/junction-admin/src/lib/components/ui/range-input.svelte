<script lang="ts">
  export let value: number = undefined;
  export let formatter: (value: number) => string = (value: number): string =>
    value?.toString() ?? "";
  export let min = 0;
  export let max = 100;
  export let label: string = undefined;
</script>

<div class="range-input">
  <label>
    <strong>{formatter(value)}</strong>

    <input type="range" bind:value {min} {max} />

    {#if !!label}<span>{label}</span>{/if}
  </label>
</div>

<style>
  .range-input {
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

  .range-input:focus-within {
    box-shadow: var(--focus-outline);
  }

  label {
    display: grid;
    grid-template-columns: 68px 1fr;
    height: 100%;
    width: 100%;
  }

  strong {
    padding: 24px 0 0 8px;
    height: 100%;
  }

  span {
    position: absolute;
    display: block;
    font-size: 12px;
    top: 5.5px;
    left: 8px;
    color: var(--color-teal);
    transition: font-size 150ms ease, top 150ms ease;
    pointer-events: none;
    user-select: none;
  }

  input {
    width: calc(100% - 8px);
    vertical-align: top;
    border: 0;
    background-color: var(--color-teal);
    margin: 28px 0 0;
    outline: 0;
    cursor: pointer;

    -webkit-appearance: none;
    appearance: none;
    height: 8px;
    border-radius: 8px;
  }

  input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background-color: var(--color-teal-lighter);
    border: 1px solid var(--color-teal);
    border-radius: 50%;
  }

  input::placeholder {
    color: var(--color-gray-dark);
  }
</style>
