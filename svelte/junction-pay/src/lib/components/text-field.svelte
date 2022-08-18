<script lang="ts" context="module">
  export type InputEvent = Event & { currentTarget: HTMLInputElement };
</script>

<script lang="ts">
  import { createEventDispatcher } from "svelte";

  type Type = $$Generic<"email" | "text" | "password" | "number">;
  type Value = Type extends "number" ? number : string;

  export let disabled = false;
  export let tabIndex = 0;
  export let readOnly = false;
  export let id: string | undefined = undefined;
  export let value: Value | undefined = "" as Value;
  export let type: Type = (typeof value === "number" ? "number" : "text") as Type;
  export let placeholder: string | undefined = undefined;
  export let error: boolean | string | undefined = undefined;
  export let maxLength: number | undefined = undefined;
  export let max: number | undefined = undefined;

  const dispatch = createEventDispatcher<{ input: InputEvent }>();

  $: hasError = !!error;
  $: errorMessage = typeof error === "string" ? error : undefined;

  function input(e: InputEvent): void {
    dispatch("input", e);

    value = (type === "number" ? Number(e.currentTarget.value) : e.currentTarget.value) as Value;
  }
</script>

<input
  on:click
  on:blur
  on:mousedown
  maxlength={maxLength}
  {max}
  {type}
  {value}
  {placeholder}
  {id}
  {disabled}
  tabindex={tabIndex}
  class="text-field"
  class:error={hasError}
  on:input={input}
  readonly={readOnly}
/>

{#if errorMessage}
  <p>{errorMessage}</p>
{/if}

<style>
  .text-field {
    background-color: var(--color-white);
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 14px;
    font-weight: 400;
    height: 44px;
    outline: 0;
    padding: 15px 14px;
    transition: border-color var(--speed-fast) ease;
  }

  .text-field::placeholder {
    color: var(--color-gray);
  }

  .text-field.text-field.text-field.error {
    border-color: var(--color-red);
  }

  p {
    color: var(--color-red);
    margin: 4px;
  }
</style>
