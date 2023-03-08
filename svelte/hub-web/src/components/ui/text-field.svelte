<script lang="ts" context="module">
  type InputEvent = Event & { currentTarget: EventTarget & HTMLInputElement };
</script>

<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";
  import { getRandomId } from "utils/common";

  type TType = $$Generic<"text" | "password" | "email" | "phone" | "number">;
  type TValue = TType extends "number" ? number : string;

  export let id: string = getRandomId("text-field-");
  export let type: TType | undefined = undefined;
  export let value: TValue | undefined = undefined;
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let error: string | boolean = false;

  const dispatch = createEventDispatcher<{ input: InputEvent }>();

  function updateValue(ev: InputEvent): void {
    if (type === "number") {
      value = parseInt(ev.currentTarget.value, 10) as TValue;
    } else {
      value = ev.currentTarget.value as TValue;
    }

    dispatch("input");
  }
</script>

<div class="text-field" class:error>
  {#if label}
    <label class="typography label-medium" for={id}>{label}</label>
  {/if}

  <div class="wrapper">
    <slot name="icon-before" />

    <input
      {id}
      class="typography label-large"
      {type}
      value={value === undefined ? "" : value}
      {placeholder}
      on:input={updateValue}
    />

    <slot name="icon-after" />
  </div>

  {#if typeof error === "string"}
    <span class="typography label-small error-message" transition:slide={{ duration: 200 }}
      >{error}</span
    >
  {/if}
</div>

<style>
  .text-field {
    display: inline-flex;
    flex-flow: column;
    gap: 4px;
    border-radius: 6px;
  }

  label {
    color: var(--color-neutral-900);
  }

  .wrapper {
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    gap: 8px;
    align-items: center;
    padding: 18px 12px;
    border: var(--color-neutral-200) 1px solid;
    border-radius: inherit;
    box-shadow: var(--shadow-xsmall);
    transition: border 200ms ease;
  }

  .error > .wrapper {
    border-color: var(--color-destructive-300);
  }

  input {
    color: var(--color-neutral-900);
    background-color: transparent;
    border: 0;
    outline: 0;
  }

  input::placeholder {
    color: var(--color-neutral-600);
  }

  .error-message {
    color: var(--color-destructive-500);
  }
</style>
