<script lang="ts">
  export let type: "button" | "reset" | "submit" = "button";
  export let variant: "fill" | "text" | "outline" = "fill";
  export let size: "small" | "medium" | "large" = "large";
  export let color: "primary" | "secondary" | "positive-gradient" = "primary";
  export let disabled = false;
</script>

<button
  {type}
  on:click
  class:fill={variant === "fill"}
  class:text={variant === "text"}
  class:outline={variant === "outline"}
  class:small={size === "small"}
  class:medium={size === "medium"}
  class:large={size === "large"}
  class:primary={color === "primary"}
  class:secondary={color === "secondary"}
  class:positive-gradient={color === "positive-gradient"}
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

  button:disabled {
    cursor: not-allowed;
    opacity: 0.2;
  }

  .medium {
    padding: 12px;
    font-weight: 500;
    line-height: 16px;
  }

  .large {
    padding: 16px;
    font-weight: 600;
    font-size: 16px;
    line-height: 24px;
  }

  .fill.primary {
    color: var(--color-generic-white);
    background-color: var(--color-primary-500);
  }

  .outline.primary {
    color: var(--color-primary-600);
    border: var(--color-primary-600) 1px solid;
  }

  .positive-gradient {
    color: var(--color-generic-white);
    background-image: var(--color-positive-gradient);
  }

  .outline {
    background-color: transparent;
  }
</style>
