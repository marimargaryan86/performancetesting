<script lang="ts">
  type Type = $$Generic<"email" | "text" | "password" | "number">;
  type Value = Type extends "number" ? number : string;

  export let disabled = false;
  export let tabIndex = 0;
  export let readOnly = false;
  export let id: string | undefined = undefined;
  export let value: Value | undefined = "" as Value;
  export let type: Type = (typeof value === "number" ? "number" : "text") as Type;
  export let placeholder: string | undefined = undefined;
  export let error = false;

  function input(e: Event & { currentTarget: EventTarget & HTMLInputElement }): void {
    value = (type === "number" ? Number(e.currentTarget.value) : e.currentTarget.value) as Value;
  }
</script>

<input
  on:click
  on:blur
  on:mousedown
  {type}
  {value}
  {placeholder}
  {id}
  {disabled}
  tabindex={tabIndex}
  class="text-field"
  class:error
  on:input={input}
  readonly={readOnly}
/>

<style>
  .text-field {
    background-color: var(--color-white);
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 14px;
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

  .text-field.text-field.text-field:focus {
    border-color: var(--color-teal);
  }
</style>
