<script lang="ts" generics="TType extends HTMLInputAttributes['type'] = 'text'">
  /* global TType */
  import Icon from "$lib/components/icons/icon.svelte";
  import { getLocale } from "$lib/i18n";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { createEventDispatcher } from "svelte";
  import { getRandomId } from "$lib/utils/random";
  import type { HTMLInputAttributes } from "svelte/elements";

  type InputEvent = Event & { currentTarget: EventTarget & HTMLInputElement };
  type TValue = TType extends "number" ? number : TType extends "date" ? Date : string;

  interface $$Props extends Omit<HTMLInputAttributes, "type" | "value" | "readonly"> {
    label?: string;
    type?: TType;
    value?: TValue;
    clearValue?: TValue;
    error?: string | string[] | boolean;
    helpText?: string;
    clearable?: boolean;
    ignorePasswordManagers?: boolean;
    readonly?: boolean;
  }

  let className: HTMLInputAttributes["class"] = undefined;

  export { className as class };
  export let id: HTMLInputAttributes["id"] = getRandomId("text-field");
  export let label: string | undefined = undefined;
  export let type: TType = "text" as TType;
  export let value: TValue | undefined = undefined;
  export let clearValue: TValue | undefined = undefined;
  export let error: string | string[] | boolean = false;
  export let required: HTMLInputAttributes["required"] = false;
  export let helpText: string | undefined = undefined;
  export let clearable = false;
  export let autocomplete: HTMLInputAttributes["autocomplete"] = undefined;
  export let disabled: HTMLInputAttributes["disabled"] = false;
  export let role: HTMLInputAttributes["role"] = "textbox";
  export let ignorePasswordManagers: boolean | undefined = undefined;
  export let readonly: boolean | undefined = undefined;

  let inputRef: HTMLInputElement;

  // Since type isn't populated directly we need to evaluate it during render
  let ignorePasswordManagersValue =
    typeof ignorePasswordManagers === "boolean"
      ? ignorePasswordManagers
      : !["password", "email"].includes(type as string);

  const locale = getLocale();
  const dispatch = createEventDispatcher<{ input: HTMLInputElement; clear: void }>();

  function onInput(event: InputEvent): void {
    error = false;

    if (type === "number") {
      value = Number(event.currentTarget.value) as TValue;
    } else if (type === "date") {
      const nextValue = new Date(event.currentTarget.value);

      if (!isNaN(nextValue.getTime())) {
        value = nextValue as TValue;
      }
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

  $: displayValue = value instanceof Date ? value.toLocaleDateString($locale) : value ?? "";
  $: displayError = error instanceof Array ? error.join(", ") : error;
  $: ariaDescribedBy = typeof displayError === "string" ? `${id}-error` : `${id}-help-text`;
</script>

<div class:text-field={true} class={className} class:error>
  {#if label}
    <label id="{id}-label" for={id}>
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
      {role}
      {disabled}
      {readonly}
      value={displayValue}
      on:click
      on:focus
      on:blur
      on:input={onInput}
      bind:this={inputRef}
      typography="body-medium"
      autocomplete={autocomplete ?? "off"}
      list={autocomplete ? "" : "autocompleteOff"}
      spellcheck={Boolean(autocomplete)}
      autocapitalize={autocomplete ? "off" : undefined}
      autocorrect={autocomplete ? "off" : undefined}
      aria-invalid={typeof displayError === "string" ? "true" : undefined}
      aria-autocomplete={autocomplete ? "list" : "none"}
      aria-describedby={ariaDescribedBy}
      aria-required={required}
      aria-labelledby={label ? `${id}-label` : undefined}
      aria-disabled={disabled}
      data-1p-ignore={ignorePasswordManagersValue}
      data-lpignore={ignorePasswordManagersValue}
      {...$$restProps}
    />

    {#if clearable && value}
      <button type="button" on:click={clear} class="clear" tabindex="-1">
        <Icon variant="remove-cross" color="var(--color-common-dark-strong)" size="12px" />
      </button>
    {/if}

    <slot name="icon-after" />
  </div>

  {#if !displayError && helpText}
    <span id="{id}-help-text" class="help-text" transition:slideFade={{ duration: 300 }}
      >{helpText}</span
    >
  {/if}

  {#if typeof displayError === "string"}
    <span id="{id}-error" class="error-message" transition:slideFade={{ duration: 300 }}
      >{displayError}</span
    >
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
    --x-border-color-focus: var(--border-color-focus, var(--color-common-line-strong));

    display: inline-flex;
    flex-flow: column;
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

  .error > .wrapper {
    border-color: #fe4e4e;
  }

  .text-field:focus-within > .wrapper {
    border-color: var(--x-border-color-focus);
  }

  .wrapper > :global(svg),
  .wrapper > :global(.icon) {
    position: absolute;
    width: 20px;
    height: 20px;
    pointer-events: none;
  }

  .wrapper > :global(svg:first-child),
  .wrapper > :global(.icon:first-child) {
    left: var(--x-icon-padding);
  }

  .wrapper > :global(svg:last-child),
  .wrapper > :global(.icon:last-child) {
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

  .error-message {
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }

  .help-text {
    margin-top: 8px;
    color: var(--color-common-light-medium);
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
