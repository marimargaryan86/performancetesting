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
  $: placeholderShowing = placeholder && !value;

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
    <span class:placeholder={placeholderShowing} class="typography body-medium">
      {displayValue ?? placeholder ?? ""}
    </span>

    {#if value && !expanded}
      <button type="button" on:click|stopPropagation={clearValue} class="clear">
        <RemoveIcon color="var(--color-main-neutral-800)" />
      </button>
    {:else}
      <ChevronIcon direction={expanded ? "up" : "down"} color="var(--color-common-light-strong)" />
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
    --x-icon-padding: var(--icon-padding, 16px);

    position: relative;
    display: inline-block;
  }

  .header {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: var(--x-height);
    padding: var(--x-icon-padding);
    white-space: nowrap;
    background-color: var(--color-common-background-light-main);
    border: 1px solid var(--color-common-line-medium);
    border-radius: 8px;
    cursor: pointer;
  }

  .header > button,
  .header > :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .placeholder {
    color: var(--color-common-light-soft);
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
