<script lang="ts">
  export let type: "button" | "reset" | "submit" | undefined = undefined;
  export let variant: "filled" | "empty" = "filled";
  let className: string | undefined = undefined;
  export { className as class };
</script>

<button {type} class:empty={variant === "empty"} class={className} on:click>
  <slot />
</button>

<style>
  button {
    background-color: var(--color-teal);
    border: transparent 1px solid;
    border-radius: 10px;
    color: var(--color-white);
    cursor: pointer;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 14px;
    font-weight: 600;
    height: 44px;
    outline: 0;
    padding: 0 14px;
  }

  button:focus {
    border-color: var(--color-teal-light);
  }

  .empty {
    background-color: transparent;
    border-radius: 0;
    height: max-content;
    padding: 0;
    width: max-content;
  }
</style>
