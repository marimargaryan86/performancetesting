<script lang="ts">
  import { keyboardInput } from "$lib/directives";
  import ChevronIcon from "$lib/icons/chevron-icon.svelte";
  import { slide } from "svelte/transition";
  import utils from "$lib/utils";
  import TextInput from "./text-input.svelte";

  type T = $$Generic;

  export let label: string = undefined;
  export let value: T = undefined;
  export let placeholder: string = undefined;
  export let items: T[] = [];
  export let valueFormatter: (item: T | string) => string | undefined = (
    item: string | undefined,
  ) => item;

  let expanded = false;
  let overlap = false;
  let options: Element;

  $: hasValue = value !== undefined && value !== null;

  const keyMapping = {
    ArrowUp: () => {
      const idx = items.findIndex((item) => item === value) - 1;

      if (idx >= 0) {
        value = items[idx];
      }

      utils.scrollIntoView(options?.children[idx]);
    },
    ArrowDown: () => {
      const idx = items.findIndex((item) => item === value) + 1;

      if (idx < items.length) {
        value = items[idx];
      }

      utils.scrollIntoView(options?.children[idx]);
    },
    Home: () => {
      const idx = 0;
      value = items[idx];

      utils.scrollIntoView(options?.children[idx]);
    },
    End: () => {
      const idx = items.length - 1;
      value = items[idx];

      utils.scrollIntoView(options?.children[idx]);
    },
    Space: () => (expanded = true),
    Escape: () => (expanded = false),
    Enter: () => (expanded = !expanded),
  };

  function select(item: T): void {
    value = item;
    expanded = false;
  }
</script>

<div
  tabindex={0}
  class="select-input"
  class:has-value={hasValue}
  class:overlap
  aria-expanded={expanded}
  on:blur={() => (expanded = false)}
  use:keyboardInput={keyMapping}
  aria-haspopup="listbox"
>
  <div class="wrapper">
    <div class="heading" on:click={() => (expanded = !expanded)}>
      <TextInput {label} value={valueFormatter(value)} {placeholder} readonly tabindex={-1} />

      <ChevronIcon />
    </div>

    {#if expanded}
      <ol
        role="listbox"
        class="options"
        bind:this={options}
        transition:slide|local={{ duration: 100 }}
        on:outroend={() => (overlap = false)}
        on:introstart={() => {
          overlap = true;
          options?.children[items.findIndex((item) => item === value)]?.scrollIntoView();
        }}
      >
        {#each items as item}
          <li
            class="option"
            role="option"
            on:click={() => select(item)}
            class:selected={item === value}
            aria-selected={item === value}
          >
            {valueFormatter(item)}
          </li>
        {/each}
      </ol>
    {/if}
  </div>
</div>

<style>
  .select-input {
    display: inline-block;
    height: 48px;
    color: var(--color-black);
    font-size: 14px;
    font-family: "Open Sans", Arial, Helvetica, sans-serif;
    outline: 0;
  }

  .select-input.overlap {
    z-index: 1;
  }

  .wrapper {
    width: 100%;
    background-color: var(--color-white);
    border: 1px solid var(--color-gray);
    border-radius: 4px;
  }

  .select-input:focus-within > .wrapper {
    box-shadow: var(--focus-outline);
  }

  .heading {
    position: relative;
    width: 100%;
    height: 46px;
    user-select: none;
    cursor: pointer;
    stroke: var(--color-teal);
  }

  .select-input > .wrapper > .heading > :global(.text-input) {
    border: 0;
    height: 100%;
    width: calc(100% - 32px);
    border-radius: 0;
    background-color: transparent;
    pointer-events: none;
  }

  .heading > :global(svg) {
    display: block;
    position: absolute;
    top: 15px;
    right: 7px;
    transition: transform 150ms ease;
  }

  .select-input[aria-expanded="true"] > .wrapper > .heading > :global(svg) {
    transform: rotateZ(180deg);
  }

  .options {
    display: block;
    padding: 4px 0;
    border-top: 1px solid var(--color-gray);
    width: 100%;
    max-height: 300px;
    overflow: auto;
  }

  .option {
    display: block;
    padding: 4px 8px;
    font-size: 14px;
    cursor: pointer;
  }

  .option:hover {
    background-color: var(--color-gray-light);
  }

  .option.selected {
    background-color: var(--color-teal);
    color: var(--color-white);
  }
</style>
