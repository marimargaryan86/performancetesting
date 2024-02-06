<script lang="ts" generics="TValue">
  /* global TValue */
  import { writable } from "svelte/store";
  import { slideFade } from "~/transitions/slide-fade";
  import { keyboard, type KeyboardParams } from "~/directives/keyboard";
  import { clickOutside } from "~/directives/click-outside";
  import { scale } from "svelte/transition";
  import type { MaybePromise } from "@sveltejs/kit";
  import TextField from "./text-field.svelte";
  import LoadingIcon from "~/components/icons/loading-icon.svelte";

  export let value: TValue | undefined;
  export let required = false;
  export let clearable = false;
  export let label: string | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let formatter: (v?: TValue) => string = (nextValue) => `${nextValue ?? ""}`;
  export let autocomplete: (q: string) => MaybePromise<TValue[]> = () => [];
  export let error: string | string[] | undefined = undefined;

  let items: TValue[] = [];
  let query = formatter(value);
  let dialog: HTMLUListElement | undefined;
  let textField: TextField | undefined;
  let searchTask: MaybePromise<TValue[]> | undefined = undefined;

  const pending = writable(false);

  $: hoveredIndex = value ? items.indexOf(value) : -1;
  $: expanded = items.length || $pending;

  async function search(event: CustomEvent<HTMLInputElement>): Promise<void> {
    $pending = true;
    value = undefined;

    const nextSearchTask = autocomplete(event.detail.value);
    searchTask = nextSearchTask;

    // Make sure the last query is the one that counts
    const nextItems = await nextSearchTask;

    if (searchTask === nextSearchTask) {
      items = nextItems;
      $pending = false;
    }
  }

  function select(item: TValue): void {
    value = item;
    query = formatter(item);
    items = [];
    textField?.focus();
  }

  function clear(): void {
    value = undefined;
  }

  function close(): void {
    query = formatter(value);
    items = [];
  }

  function scrollToOption(): void {
    dialog?.children[hoveredIndex]?.scrollIntoView({ block: "nearest" });
  }

  function setHoveredIndex(option?: TValue): void {
    hoveredIndex = option ? items.indexOf(option) : -1;
  }

  const keyMapping = {
    ArrowUp: (event): void => {
      hoveredIndex = Math.max(0, hoveredIndex - 1);

      if (expanded) {
        event.preventDefault();
        scrollToOption();
      } else {
        const nextValue = items[hoveredIndex];
        if (nextValue) {
          select(nextValue);
        }
      }
    },
    ArrowDown: (event): void => {
      hoveredIndex = Math.min(items.length - 1, hoveredIndex + 1);

      if (expanded) {
        event.preventDefault();
        scrollToOption();
      } else {
        const nextValue = items[hoveredIndex];

        if (nextValue) {
          select(nextValue);
        }
      }
    },
    Enter: (event): void => {
      if (expanded) {
        event.preventDefault();
        event.stopPropagation();
        const nextValue = items[hoveredIndex];

        if (nextValue) {
          return select(nextValue);
        }

        close();
      }
    },
    Escape: close,
  } satisfies KeyboardParams;
</script>

<div class="autocomplete-field" use:clickOutside={close} use:keyboard={keyMapping}>
  <TextField
    {label}
    {required}
    {placeholder}
    bind:value={query}
    {clearable}
    {error}
    on:clear={clear}
    on:input={search}
    on:blur={close}
    bind:this={textField}
  />

  {#if expanded}
    <ul
      typography="body-medium"
      class="options"
      transition:scale={{ duration: 150, start: 0.8 }}
      bind:this={dialog}
      tabindex="-1"
    >
      {#if $pending}
        <li class="loading" transition:slideFade={{ duration: 200 }}>
          <LoadingIcon color="var(--color-main-primary-600)" />
        </li>
      {/if}
      {#each items as item, idx}
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <li
          class="option"
          on:pointerover={setHoveredIndex.bind(setHoveredIndex, item)}
          on:mousedown={select.bind(select, item)}
          class:selected={item === value}
          class:hovered={hoveredIndex === idx}
        >
          {formatter(item)}
        </li>
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

  .option {
    padding: 16px;
    cursor: pointer;
    user-select: none;
  }

  .option.selected {
    background-color: var(--color-main-neutral-50);
  }

  .option.hovered {
    background-color: var(--color-main-primary-50);
  }

  .loading {
    display: flex;
    align-items: ceter;
    justify-content: center;
    padding: 16px;
  }

  .option:not(:last-child),
  .loading:not(:last-child) {
    border-bottom: 1px solid var(--color-common-line-soft);
  }
</style>
