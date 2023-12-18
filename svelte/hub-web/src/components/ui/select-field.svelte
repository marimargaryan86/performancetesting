<script lang="ts" generics="TValue">
  /* global TValue */
  import type { DirectionY } from "models/spatial";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import TextField from "./text-field.svelte";
  import { scale } from "svelte/transition";
  import { clickOutside } from "directives/click-outside";
  import { createEventDispatcher } from "svelte";
  import { keyboard } from "directives/keyboard";

  let className: string | undefined = undefined;

  const dispatch = createEventDispatcher<{ select: TValue | undefined }>();

  export let direction: DirectionY = "down";
  export { className as class };
  export let value: TValue | undefined = undefined;
  export let options: Readonly<(TValue | undefined)[]>;
  export let formatter: (nextValue?: TValue, selected?: boolean) => string | undefined = (
    nextValue,
  ) => String(nextValue ?? "");
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let required = false;
  export let error: string | string[] | boolean = false;
  export let dialogMinWidth: string | undefined = undefined;
  export let search: ((query: string, option?: TValue) => boolean) | undefined = undefined;
  export let readonly = false;

  let expanded = false;
  let selectedDisplayValue = formatter(value, true);
  let dialog: HTMLUListElement | undefined;
  let textField: TextField | undefined;

  $: filteredOptions = options;
  $: hoveredIndex = filteredOptions.indexOf(value);
  $: filter(selectedDisplayValue);
  $: if (dialog) {
    scrollToOption();
  }

  function input(): void {
    value = undefined;
    open();
  }

  function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }

  function filter(query?: string): void {
    if (!expanded) {
      return;
    }

    filteredOptions =
      search && query?.length ? options.filter((option) => search?.(query ?? "", option)) : options;
  }

  function open(): void {
    expanded = true;
    filteredOptions = options;
  }

  function close(): void {
    expanded = false;
    selectedDisplayValue = formatter(value, true);
    setHoveredIndex(value);
  }

  function select(option?: TValue): void {
    error = false;
    value = option;
    selectedDisplayValue = formatter(value, true);
    dispatch("select", value);
    close();
    textField?.focus();
  }

  function scrollToOption(): void {
    dialog?.children[hoveredIndex]?.scrollIntoView({ block: "nearest" });
  }

  function setHoveredIndex(option?: TValue): void {
    hoveredIndex = filteredOptions.indexOf(option);
  }

  const keyMapping = {
    ArrowUp: (): void => {
      hoveredIndex = Math.max(0, hoveredIndex - 1);

      if (expanded) {
        scrollToOption();
      } else {
        select(filteredOptions[hoveredIndex]);
      }
    },
    ArrowDown: (): void => {
      hoveredIndex = Math.min(filteredOptions.length - 1, hoveredIndex + 1);

      if (expanded) {
        scrollToOption();
      } else {
        select(filteredOptions[hoveredIndex]);
      }
    },
    " ": open,
    Enter: (): void => {
      if (expanded) {
        return select(filteredOptions[hoveredIndex]);
      }

      open();
    },
    Escape: close,
  };
</script>

<div
  class="select-field {className ? className : ''}"
  class:direction-up={direction === "up"}
  use:clickOutside={close}
  use:keyboard={keyMapping}
>
  <TextField
    {required}
    {label}
    {placeholder}
    readonly={readonly || !search}
    on:input={input}
    on:click={toggle}
    on:blur={close}
    bind:value={selectedDisplayValue}
    bind:this={textField}
    {error}
  >
    <ChevronIcon slot="icon-after" direction={expanded ? "up" : "down"} />
  </TextField>

  {#if expanded && filteredOptions.length}
    <ul
      class="typography body-medium options"
      style:min-width={dialogMinWidth}
      transition:scale={{ duration: 150, start: 0.8 }}
      bind:this={dialog}
      tabindex="-1"
    >
      {#each filteredOptions as option, idx}
        {@const displayValue = formatter(option)}
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <li
          class="option"
          on:mousedown={select.bind(select, option)}
          on:pointerover={setHoveredIndex.bind(setHoveredIndex, option)}
          title={displayValue}
          class:selected={option === value}
          class:hovered={hoveredIndex === idx}
        >
          <pre>{displayValue}</pre>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .select-field {
    --x-height: var(--height, 52px);

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
    z-index: var(--z-index-ui-dialog);
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

  .select-field.direction-up .options {
    top: unset;
    bottom: calc(var(--x-height) + 4px);
    transform-origin: bottom center;
  }

  .option {
    padding: 16px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    cursor: pointer;
    user-select: none;
  }

  .option.selected {
    background-color: var(--color-main-neutral-50);
  }

  .option.hovered {
    background-color: var(--color-main-primary-50);
  }

  .option:not(:last-child) {
    border-bottom: 1px solid var(--color-common-line-soft);
  }
</style>
