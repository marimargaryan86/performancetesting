<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";
  import { getRandomId } from "utils/random";

  type InputEvent = Event & { currentTarget: EventTarget & HTMLInputElement };
  type TType = $$Generic<"text" | "password" | "email" | "number">;
  type TValue = TType extends "number" ? number : string;

  export let id = getRandomId("text-field");
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let type: TType = "text" as TType;
  export let value: TValue | undefined = undefined;
  export let error: string | boolean = false;

  let inputRef: HTMLInputElement;

  const dispatch = createEventDispatcher<{ input: HTMLInputElement }>();

  function onInput(event: InputEvent): void {
    if (type === "number") {
      value = Number(event.currentTarget.value) as TValue;
    }

    value = event.currentTarget.value as TValue;

    dispatch("input", event.currentTarget);
  }

  export function focus(): void {
    inputRef.focus();
  }

  $: displayValue = value ?? "";
</script>

<div class="text-field" class:error>
  {#if label}
    <label for={id}>{label}</label>
  {/if}

  <div
    class="wrapper"
    class:icon-before={$$slots["icon-before"]}
    class:icon-after={$$slots["icon-after"]}
  >
    <slot name="icon-before" />

    <input {id} {type} value={displayValue} on:input={onInput} {placeholder} bind:this={inputRef} />

    <slot name="icon-after" />
  </div>

  {#if typeof error === "string"}
    <span class="error-message" transition:slide|local={{ duration: 300 }}>{error}</span>
  {/if}
</div>

<style>
  .text-field {
    --x-height: var(--height, 52px);
    --x-icon-padding: var(--icon-padding, 12px);
    --x-font-size: var(--font-size, 14px);

    display: inline-flex;
    flex-flow: column;
    gap: 4px;
  }

  label {
    color: var(--color-neutral-900);
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
    letter-spacing: 0.5px;
  }

  .wrapper {
    position: relative;
    display: flex;
    align-items: center;
    height: var(--x-height);
    background: var(--color-generic-white);
    border: 1px solid var(--color-neutral-200);
    border-radius: 8px;
    box-shadow: var(--shadow-xsmall);
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
    color: var(--color-neutral-900);
    font-weight: 400;
    font-size: var(--x-font-size);
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    letter-spacing: 0.1px;
    background-color: transparent;
    border: 0;
    border-radius: inherit;
    outline: 0;
  }

  input::placeholder {
    color: var(--color-neutral-400);
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
    color: #fe4e4e;
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
