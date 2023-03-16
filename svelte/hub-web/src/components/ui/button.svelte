<script lang="ts">
  export let type: "button" | "reset" | "submit" = "button";
  export let style: "fill" | "text" | "outline" = "fill";
  export let size: "small" | "medium" | "large" = "large";
  export let color: "primary" | "secondary" = "primary";
  export let disabled = false;
</script>

<button
  {type}
  on:click
  class:fill={style === "fill"}
  class:text={style === "text"}
  class:outline={style === "outline"}
  class:small={size === "small"}
  class:medium={size === "medium"}
  class:large={size === "large"}
  class:primary={color === "primary"}
  class:secondary={color === "secondary"}
  {disabled}
>
  <slot />
</button>

<style>
  button {
    padding: 0;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    letter-spacing: 0.15px;
    background-color: transparent;
    border: 0;
    border-radius: 6px;
    cursor: pointer;
    transition: opacity 150ms ease;
  }

  .fill {
    border: 1px solid transparent;
  }

  .large {
    padding: 16px;
    font-weight: 600;
    font-size: 16px;
    line-height: 24px;
  }

  .primary {
    color: var(--color-generic-white);
    background-color: var(--color-primary-500);
  }

  .primary:disabled {
    cursor: not-allowed;
    opacity: 0.2;
  }
</style>
