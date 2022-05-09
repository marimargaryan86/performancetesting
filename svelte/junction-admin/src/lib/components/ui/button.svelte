<script lang="ts">
  export let type: "normal" | "delete" | "busy" = "normal";
  export let disabled = false;
  export let submit = false;
</script>

<button
  on:click
  type={submit ? "submit" : "button"}
  class:normal={type === "normal"}
  class:delete={type === "delete"}
  class:busy={type === "busy"}
  {disabled}
>
  <slot />
</button>

<style>
  button {
    display: inline-block;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 16px;
    font-family: "Open Sans", Arial, Helvetica, sans-serif;
    border-radius: 4px;
    height: 48px;
    cursor: pointer;
    transition: background-color 150ms ease, border 150ms ease, color 150ms ease;
    user-select: none;
    outline: none;
  }

  button:focus {
    box-shadow: var(--focus-outline-dark);
  }

  button.delete:focus {
    box-shadow: var(--focus-outline-red);
  }

  button > :global(*:not(:last-child)) {
    margin-right: 4px;
  }

  button > :global(*) {
    vertical-align: middle;
  }

  button.normal {
    background-color: var(--color-teal);
    border: 1px solid var(--color-teal);
    color: var(--color-white);
    fill: var(--color-white);
  }

  button.delete {
    background-color: var(--color-red);
    border: 1px solid var(--color-red);
    color: var(--color-white);
    fill: var(--color-white);
  }

  button.busy {
    background-color: var(--color-teal-light);
    border: 1px solid var(--color-teal-light);
    color: var(--color-white);
    fill: var(--color-white);
  }

  button:disabled {
    background-color: var(--color-gray);
    border: 1px solid var(--color-gray);
    color: var(--color-gray-dark);
    fill: var(--color-gray-dark);
  }
</style>
