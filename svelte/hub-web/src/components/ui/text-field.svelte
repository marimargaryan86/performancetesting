<script
  lang="ts"
  generics="TType extends 'text' | 'tel' | 'password' | 'email' | 'number' | 'date' = 'text'"
>
  /* global TType */
  import { slideFade } from "transitions/slide-fade";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import { createEventDispatcher } from "svelte";
  import { getRandomId } from "utils/random";

  type InputEvent = Event & { currentTarget: EventTarget & HTMLInputElement };
  type TValue = TType extends "number" ? number : TType extends "date" ? Date : string;

  let className: string | undefined = undefined;

  export { className as class };
  export let id = getRandomId("text-field");
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let type: TType = "text" as TType;
  export let value: TValue | undefined = undefined;
  export let clearValue: TValue | undefined = undefined;
  export let error: string | string[] | boolean = false;
  export let name: string | undefined = undefined;
  export let readonly = false;
  export let required = false;
  export let helpText: string | undefined = undefined;
  export let clearable = false;
  export let maxLength: number | undefined = undefined;

  let inputRef: HTMLInputElement;

  const dispatch = createEventDispatcher<{ input: HTMLInputElement; clear: void }>();

  function onInput(event: InputEvent): void {
    error = false;

    if (type === "number") {
      value = Number(event.currentTarget.value) as TValue;
    } else if (type === "date") {
      const nextValue = new Date(event.currentTarget.value);

      value = isNaN(nextValue.getTime()) ? undefined : (nextValue as TValue);
    } else {
      value = event.currentTarget.value as TValue;
    }

    dispatch("input", event.currentTarget);
  }

  function clear(): void {
    value = clearValue;
    dispatch("clear");
  }

  export function focus(): void {
    inputRef.focus();
  }

  $: displayValue = value instanceof Date ? value.toLocaleDateString("sv-SE") : value ?? "";
  $: displayError = error instanceof Array ? error.join(", ") : error;
</script>

<div class:text-field={true} class={className} class:error>
  {#if label}
    <label for={id}>
      {label}
      {#if required}
        <span>*</span>
      {/if}
    </label>
  {/if}

  <div
    class="wrapper"
    class:icon-before={$$slots["icon-before"]}
    class:icon-after={$$slots["icon-after"]}
  >
    <slot name="icon-before" />

    <input
      {id}
      {type}
      {name}
      {readonly}
      {placeholder}
      maxlength={maxLength}
      value={displayValue}
      on:click
      on:focus
      on:blur
      on:input={onInput}
      bind:this={inputRef}
      class="typography body-medium"
    />

    {#if clearable && value}
      <button type="button" on:click={clear} class="clear">
        <RemoveIcon color="var(--color-common-dark-strong)" />
      </button>
    {/if}

    <slot name="icon-after" />
  </div>

  {#if !displayError && helpText}
    <span class="help-text" transition:slideFade={{ duration: 300 }}>{helpText}</span>
  {/if}

  {#if typeof displayError === "string"}
    <span class="error-message" transition:slideFade={{ duration: 300 }}>{displayError}</span>
  {/if}
</div>

<style>
  .text-field {
    --x-height: var(--height, 52px);
    --x-icon-padding: var(--icon-padding, 16px);
    --x-font-size: var(--font-size, 14px);
    --x-label-font-size: var(--label-font-size, 12px);
    --x-label-font-weight: var(--label-font-weight, 400);
    --x-label-font-family: var(--label-font-family, Poppins);
    --x-border-color: var(--border-color, var(--color-common-line-medium));

    display: inline-flex;
    flex-flow: column;
  }

  .text-field:focus-within {
    --x-border-color: var(--color-common-line-strong);
  }

  label {
    margin-bottom: 8px;
    color: var(--color-main-neutral-900);
    font-weight: var(--x-label-font-weight);
    font-size: var(--x-label-font-size);
    font-family: var(--x-label-font-family);
    font-style: normal;
  }

  label > span {
    color: var(--color-main-primary-500);
  }

  .wrapper {
    position: relative;
    display: flex;
    align-items: center;
    height: var(--x-height);
    background: var(--color-common-background-light-main);
    border: 1px solid var(--x-border-color);
    border-radius: 8px;
    transition: border 150ms ease;
  }

  .wrapper > :global(svg) {
    position: absolute;
    width: 20px;
    height: 20px;
    pointer-events: none;
  }

  .wrapper > :global(svg:first-child) {
    left: var(--x-icon-padding);
  }

  .wrapper > :global(svg:last-child) {
    right: var(--x-icon-padding);
  }

  input {
    display: block;
    grid-column: 2;
    width: 100%;
    height: 100%;
    padding: 0 var(--x-icon-padding);
    color: var(--color-common-light-strong);
    background-color: transparent;
    border: 0;
    border-radius: inherit;
    outline: 0;
    cursor: inherit;
    transition: padding 150ms ease;
  }

  input::placeholder {
    color: var(--color-common-light-soft);
    transition: opacity 150ms ease;
  }

  .clear {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: calc(var(--x-height) * 0.4);
    height: calc(var(--x-height) * 0.4);
    margin-right: var(--x-icon-padding);
    padding: 8px 2px;
    background-color: var(--color-main-neutral-400);
    border: 0;
    border-radius: 50%;
    cursor: pointer;
  }

  .clear > :global(svg) {
    width: calc(var(--x-height) * 0.2);
    height: calc(var(--x-height) * 0.2);
  }

  .wrapper.icon-before > input {
    padding-left: calc(var(--x-icon-padding) + 28px);
  }

  .wrapper.icon-after > input {
    padding-right: calc(var(--x-icon-padding) + 28px);
  }

  .error > .wrapper {
    border-color: #fe4e4e;
  }

  .error-message {
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }

  .help-text {
    color: var(--color-common-light-medium);
    font-weight: 400;
    font-size: 12px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    line-height: 1.3;
  }
</style>
