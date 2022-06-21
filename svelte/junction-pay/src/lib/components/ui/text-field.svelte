<script lang="ts">
  type Type = $$Generic<"email" | "text" | "password" | "number">;
  type Value = Type extends "number" ? number : string;

  export let id: string | undefined = undefined;
  export let value: Value | undefined = undefined;
  export let type: Type = (typeof value === "number" ? "number" : "text") as Type;
  export let placeholder: string | undefined = undefined;
  export let error = false;

  function input(e: Event & { currentTarget: EventTarget & HTMLInputElement }): void {
    value = (type === "number" ? Number(e.currentTarget.value) : e.currentTarget.value) as Value;
  }
</script>

<input {type} {value} {placeholder} {id} class="text-field" class:error on:input={input} />

<style>
  input {
    background-color: var(--color-white);
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 14px;
    height: 44px;
    outline: 0;
    padding: 15px 14px;
    transition: border-color 150ms ease;
  }

  input::placeholder {
    color: var(--color-gray);
  }

  .error {
    border-color: var(--color-red);
  }
</style>
