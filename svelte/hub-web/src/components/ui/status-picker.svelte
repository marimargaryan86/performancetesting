<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import { scale } from "svelte/transition";
  import { getRandomId } from "utils/random";
  import Checkbox from "./checkbox.svelte";

  type TStatus = $$Generic<string>;

  export let value: Readonly<TStatus>[] | undefined = undefined;
  export let statuses: Readonly<TStatus[]>;
  export let placeholder: string | undefined = undefined;
  export let format: (status: TStatus) => string = (status) => status;

  let expanded = false;

  $: displayValue = value?.length
    ? value.map((status) => format(status)).join(", ")
    : placeholder ?? "";

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }

  function clearValue(): void {
    value = [];
  }
</script>

<div class="status-picker" use:clickOutside={close}>
  <button class="header" on:click={toggle} type="button">
    <span>{displayValue}</span>

    {#if value?.length && !expanded}
      <button type="button" on:click|stopPropagation={clearValue} class="clear">
        <RemoveIcon color="var(--color-neutral-800)" />
      </button>
    {:else}
      <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-neutral-900)" />
    {/if}
  </button>

  {#if expanded}
    <ul class="dialogue" transition:scale|local={{ duration: 150, start: 0.8 }}>
      {#each statuses as status}
        {@const id = getRandomId("status")}

        <li>
          <Checkbox bind:group={value} value={status} {id} />

          <label for={id}>{format(status)}</label>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .status-picker {
    --x-height: var(--height, 52px);
    --x-font-size: var(--font-size, 14px);
    --x-icon-padding: var(--icon-padding, 12px);

    position: relative;
    display: inline-block;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    height: var(--x-height);
    padding: var(--x-icon-padding);
    color: var(--color-neutral-900);
    font-weight: 400;
    font-size: var(--x-font-size);
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    letter-spacing: 0.1px;
    background-color: var(--color-generic-white);
    border: 1px solid var(--color-neutral-200);
    border-radius: 8px;
    box-shadow: var(--shadow-xsmall);
    cursor: pointer;
  }

  .header > button,
  .header > :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .dialogue {
    position: absolute;
    top: 100%;
    left: 0;
    z-index: 100;
    margin-top: 4px;
    padding: 8px;
    color: var(--color-neutral-800);
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 14px;
    white-space: nowrap;
    background: #ffffff;
    border: var(--color-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgb(17 24 39 / 0.05), 0 12px 16px rgb(17 24 39 / 0.1);
    transform-origin: top left;
  }

  li {
    display: flex;
    align-items: center;
    margin: 0 -8px;
    padding: 0 12px;
    user-select: none;
  }

  li:hover {
    background-color: var(--color-neutral-50);
  }

  label {
    flex-grow: 1;
    padding: 8px;
    cursor: pointer;
  }

  .clear {
    padding: 8px 2px;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .clear > :global(svg) {
    vertical-align: middle;
  }
</style>
