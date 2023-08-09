<script lang="ts" generics="TValue">
  /* global TValue */
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import TextField from "./text-field.svelte";
  import { scale } from "svelte/transition";
  import { clickOutside } from "directives/click-outside";

  let className: string | undefined = undefined;

  export { className as class };
  export let value: TValue | undefined = undefined;
  export let options: TValue[];
  export let formatter: (nextValue?: TValue) => string = (nextValue) => String(nextValue ?? "");
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let required = false;
  export let scroll = false;
  export let error: string | boolean = false;

  let expanded = false;

  function toggleExpanded(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function select(option: TValue): void {
    value = option;
    close();
  }
</script>

<div class="select-field {className ? className : ''}" use:clickOutside={close}>
  <TextField
    {required}
    {label}
    {placeholder}
    readonly
    on:click={toggleExpanded}
    value={formatter(value)}
    {error}
  >
    <ChevronIcon slot="icon-after" direction={expanded ? "up" : "down"} />
  </TextField>

  {#if expanded}
    <ul
      class="typography body-medium options"
      class:scroll
      transition:scale={{ duration: 150, start: 0.8 }}
    >
      {#each options as option}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
        <li class="option" on:click={select.bind(select, option)}>{formatter(option)}</li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .select-field {
    position: relative;
    display: inline-block;
  }

  .select-field > :global(.text-field) {
    width: 100%;
    vertical-align: top;
    cursor: pointer;
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

  .scroll {
    height: 107px;
    overflow: scroll;
  }
</style>
