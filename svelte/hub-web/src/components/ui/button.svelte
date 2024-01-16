<script lang="ts">
  /* global Typography */
  let className: string | undefined = undefined;
  export { className as class };
  export let type: "button" | "reset" | "submit" = "button";
  export let disabled = false;
  export let variant: "primary" | "outline" | "text" = "primary";
  export let size: "large" | "medium" | "small" | "x-small" | "xx-small" = "large";
  export let href: string | undefined = undefined;
  export let minWidth: string | undefined = undefined;
  export let preload = true;
  export let download: string | boolean | undefined = undefined;
  export let value: string | undefined = undefined;
  export let name: string | undefined = undefined;

  let ref: HTMLButtonElement | HTMLAnchorElement | undefined;

  export function getRef(): typeof ref {
    return ref;
  }

  $: typography = getTypography(size);

  function getTypography(nextSize: typeof size): Typography {
    if (nextSize === "large" || nextSize === "medium") {
      return "body-large";
    }

    return "body-medium";
  }
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<svelte:element
  this={href ? "a" : "button"}
  bind:this={ref}
  {href}
  {type}
  {disabled}
  {download}
  {value}
  {name}
  data-sveltekit-preload-data={!href || preload ? undefined : "off"}
  on:click
  style:min-width={minWidth}
  class={className}
  weight="bold"
  {typography}
  class:primary={variant === "primary"}
  class:outline={variant === "outline"}
  class:text={variant === "text"}
  class:large={size === "large"}
  class:medium={size === "medium"}
  class:small={size === "small"}
  class:x-small={size === "x-small"}
  class:xx-small={size === "xx-small"}
>
  <slot />
</svelte:element>

<style>
  button,
  a {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    justify-content: center;
    color: var(--color);
    font-family: Inter, Arial, Helvetica, sans-serif;
    text-decoration: none;
    background-color: var(--background-color);
    border: 0;
    border-radius: 8px;
    outline: 0;
    box-shadow: 0 0 0 var(--border-width) var(--border-color) inset;
    cursor: pointer;
    transition:
      padding 150ms ease,
      color 150ms ease,
      background-color 150ms ease,
      border 150ms ease,
      box-shadow 150ms ease;
  }

  .primary {
    --color: var(--color-common-dark-strong);
    --icon-color: var(--color-common-dark-strong);
    --background-color: var(--color-main-primary-500);
    --border-color: transparent;
    --border-width: 0;
  }

  .primary:focus {
    --border-color: var(--color-main-primary-800);
    --border-width: 2px;
  }

  .primary:hover {
    --background-color: var(--color-main-primary-700);
  }

  .primary:disabled {
    --color: var(--color-main-neutral-400);
    --background-color: var(--color-main-neutral-50);
    --icon-color: var(--color-main-neutral-400);
  }

  .outline {
    --color: var(--color-common-light-strong);
    --icon-color: var(--color-main-primary-500);
    --background-color: transparent;
    --border-color: var(--color-main-primary-400);
    --border-width: 1px;
  }

  .outline:focus {
    --border-color: var(--color-main-primary-500);
    --border-width: 2px;
    --background-color: var(--color-common-background-light-main);
  }

  .outline:hover {
    --border-color: var(--color-main-primary-500);
    --background-color: rgb(75 182 156 / 0.2);
  }

  .outline:disabled {
    --color: var(--color-main-neutral-400);
    --background-color: transparent;
    --icon-color: var(--color-main-neutral-400);
    --border-color: var(--color-main-neutral-100);
  }

  .text {
    --color: var(--color-common-light-strong);
    --icon-color: var(--color-main-primary-500);
    --background-color: transparent;
    --border-color: transparent;
    --border-width: 0;
  }

  .text:focus {
    --background-color: var(--color-main-primary-200);
  }

  .text:hover {
    --background-color: rgb(75 182 156 / 0.2);
  }

  .text:disabled {
    --color: var(--color-main-neutral-400);
    --icon-color: var(--color-main-neutral-400);
    --background-color: transparent;
  }

  .large {
    --icon-size: 24px;

    height: 52px;
    padding: 15px 24px;
  }

  .medium {
    --icon-size: 20px;

    padding: 11px 24px;
  }

  .small {
    --icon-size: 20px;

    padding: 10px 16px;
  }

  .x-small {
    --icon-size: 20px;

    padding: 6px 16px;
  }

  .xx-small {
    --icon-size: 20px;

    padding: 6px 8px;
  }

  button > :global(svg),
  a > :global(svg) {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: var(--icon-size);
    height: var(--icon-size);
  }

  button :global(div.icon),
  a :global(div.icon) {
    background-color: var(--icon-color);
    transition: background-color 150ms ease;
  }
</style>
