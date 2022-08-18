<script lang="ts">
  import clickOutside from "$lib/actions/click-outside";
  import keyBinding from "$lib/actions/key-binding";
  import { afterUpdate } from "svelte";
  import { slide } from "svelte/transition";
  import TextField from "./text-field.svelte";

  type TValue = $$Generic<{ toString: () => string }>;

  export let value: TValue | undefined = undefined;
  export let items: TValue[] = [];
  export let placeholder: string | undefined = undefined;
  export let id: string | undefined = undefined;
  export let tabIndex = 0;
  export let error = false;
  export let disabled = false;

  let container: HTMLDivElement;
  let itemContainer: HTMLDivElement;
  let expanded = false;
  let partiallyExpanded = false;

  $: selectedIdx = value ? items.indexOf(value) : -1;

  function toggle(): void {
    expanded = !expanded;
  }

  function collapse(): void {
    expanded = false;
  }

  function expand(): void {
    expanded = true;
  }

  function select(item: TValue): void {
    container.focus();
    value = item;
    collapse();
  }

  function scrollIntoView(): void {
    const selectedNode = itemContainer?.querySelector("[aria-selected='true']");

    if (!selectedNode) {
      return;
    }

    selectedNode.scrollIntoView({ block: "nearest" });
  }

  function previousItem(): void {
    value = items[Math.max(0, selectedIdx - 1)];
  }

  function nextItem(): void {
    value = items[Math.min(items.length - 1, selectedIdx + 1)];
  }

  function expanding(): void {
    partiallyExpanded = true;
  }

  function collapsed(): void {
    partiallyExpanded = false;
  }

  function blur(e: FocusEvent): void {
    if (!container.contains(e.relatedTarget as Node)) {
      collapse();
    }
  }

  afterUpdate(() => {
    scrollIntoView();
  });
</script>

<div
  bind:this={container}
  tabindex={tabIndex}
  class="select-field"
  class:error
  use:clickOutside={collapse}
  aria-expanded={partiallyExpanded}
  class:expanded
  {id}
  on:blur={blur}
  role="listbox"
  use:keyBinding={{
    Enter: toggle,
    Space: expand,
    Escape: collapse,
    ArrowUp: previousItem,
    ArrowDown: nextItem,
    Home: () => (value = items[0]),
    End: () => (value = items[items.length - 1]),
  }}
>
  <div class="head" on:click={toggle} role="button">
    <slot name="head" {value}>
      <TextField value={value?.toString() ?? ""} readOnly {placeholder} tabIndex={-1} {disabled} />
    </slot>
  </div>

  {#if expanded}
    <div
      class="body"
      transition:slide={{ duration: 150 }}
      on:introstart={expanding}
      on:outroend={collapsed}
      bind:this={itemContainer}
      tabindex={-1}
    >
      <slot name="body" {select} {items} {value}>
        <ul class="options">
          {#each items as item}
            <li
              class="option"
              aria-selected={item === value}
              on:click={() => select(item)}
              role="option"
            >
              {item.toString()}
            </li>
          {/each}
        </ul>
      </slot>
    </div>
  {/if}
</div>

<style>
  .select-field {
    background-color: var(--color-white);
    border-color: var(--color-gray-lightest);
    border-radius: 10px;
    display: inline-block;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 16px;
    height: 44px;
    outline: 0;
    transition: border-color var(--speed-fast) ease;
  }

  .select-field.select-field.error {
    border-color: var(--color-red);
  }

  .select-field:not(.expanded):focus {
    border-color: var(--color-teal);
  }

  .select-field[aria-expanded="true"] {
    filter: drop-shadow(0 4px 12px rgb(0 0 0 / 12%));
    position: relative;
    z-index: 1;
  }

  .select-field.expanded {
    z-index: 2;
  }

  .head {
    align-items: center;
    background-color: inherit;
    border: 1px solid;
    border-color: inherit;
    border-radius: inherit;
    cursor: pointer;
    display: flex;
    font-size: inherit;
    height: 100%;
    justify-content: space-between;
  }

  .select-field[aria-expanded="true"] > .head {
    border-bottom-color: transparent;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  .head::after {
    border: 0 solid var(--color-gray-lighter);
    border-width: 2px 2px 0 0;
    content: "";
    display: block;
    height: 8px;
    margin-right: 14px;
    transform: translateY(-20%) rotateZ(135deg);
    transition: transform var(--speed-fast) ease;
    width: 8px;
  }

  .select-field[aria-expanded="true"] > .head::after {
    transform: translateY(20%) rotateZ(315deg);
  }

  .head > :global(.text-field) {
    background-color: transparent;
    border: transparent;
    cursor: pointer;
    font-family: inherit;
    font-size: inherit;
    padding-left: 21px;
    padding-right: 21px;
    pointer-events: none;
    vertical-align: top;
    width: 100%;
  }

  .body {
    background-color: var(--color-white);
    border: 1px solid;
    border-color: inherit;
    border-radius: 0 0 10px 10px;
    border-top: var(--color-gray-lightest) 1px solid;
    float: left;
    font-size: inherit;
    left: 0;
    max-height: 300px;
    overflow-y: auto;
    position: relative;
    width: 100%;
  }

  .option {
    cursor: pointer;
    font-size: inherit;
    padding: 19px 21px;
  }

  .option[aria-selected="true"] {
    background-color: var(--color-gray-lightest);
  }

  .option:hover {
    background-color: var(--color-light-background);
  }
</style>
