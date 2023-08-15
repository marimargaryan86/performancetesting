<script lang="ts" generics="TValue">
  import { clickOutside } from "directives/click-outside";

  import { scale } from "svelte/transition";

  /* global TValue */
  import type { MaybePromise } from "@sveltejs/kit";
  import TextField from "./text-field.svelte";

  export let value: TValue | undefined;
  export let required = false;
  export let clearable = false;
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let formatter: (v?: TValue) => string = (nextValue) => `${nextValue ?? ""}`;
  export let autocomplete: (q: string) => MaybePromise<TValue[]> = () => [];

  let items: TValue[] = [];
  let query = formatter(value);

  $: expanded = items.length;

  async function search(event: CustomEvent<HTMLInputElement>): Promise<void> {
    value = undefined;
    items = await autocomplete(event.detail.value);
  }

  function select(item: TValue): void {
    value = item;
    query = formatter(item);
    items = [];
  }

  function clear(): void {
    value = undefined;
  }

  function close(): void {
    items = [];
  }
</script>

<div class="autocomplete-field" use:clickOutside={close}>
  <TextField
    {label}
    {required}
    {placeholder}
    bind:value={query}
    {clearable}
    on:clear={clear}
    on:input={search}
  />

  {#if expanded}
    <ul class="options typography body-medium" transition:scale={{ duration: 150, start: 0.8 }}>
      {#each items as item}
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <li class="option" on:click={select.bind(select, item)} on:keypress>{formatter(item)}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .autocomplete-field {
    position: relative;
    display: inline-flex;
  }

  .autocomplete-field > :global(.text-field) {
    width: 100%;
    vertical-align: top;
  }

  .options {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    z-index: 2;
    width: 100%;
    max-height: 400px;
    overflow-y: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: 1px solid var(--color-common-line-medium);
    border-radius: 8px;
    box-shadow: 0 0 12px rgb(0 0 0 / 0.2);
    transform-origin: top center;
    transition: border 150ms ease;
  }

  .option {
    padding: 16px;
    cursor: pointer;
    user-select: none;
  }

  .option:not(:last-child) {
    border-bottom: 1px solid var(--color-common-line-soft);
  }
</style>
