<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import { yymmdd } from "formatting/date-time";
  import type { DateRange } from "models/date-time";
  import Dialogue from "./dialogue.svelte";

  type TRange = $$Generic<boolean>;
  type TValue = TRange extends true ? DateRange : Date;

  export let range: TRange;
  export let value: TValue | undefined = undefined;
  export let placeholder: string | undefined = undefined;

  let expanded = false;
  let displayValue = getFormattedValue();

  $: value, (displayValue = getFormattedValue());

  function getFormattedValue(): string | undefined {
    if (!value) {
      return undefined;
    }

    if (value instanceof Date) {
      return yymmdd(value);
    }

    if (value.from && value.to) {
      return `${yymmdd(value.from)} - ${yymmdd(value.to)}`;
    }

    return undefined;
  }

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
    value = undefined;
  }
</script>

<div class="date-picker" use:clickOutside={close}>
  <button class="header" on:click={toggle} type="button">
    <span>{displayValue ?? placeholder ?? ""}</span>

    {#if value && !expanded}
      <button type="button" on:click|stopPropagation={clearValue} class="clear">
        <RemoveIcon color="var(--color-neutral-800)" />
      </button>
    {:else}
      <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-neutral-900)" />
    {/if}
  </button>

  {#if expanded}
    <Dialogue {range} bind:value />
  {/if}
</div>

<style>
  .date-picker {
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
