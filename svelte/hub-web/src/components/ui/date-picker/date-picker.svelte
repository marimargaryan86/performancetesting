<script lang="ts" generics="TRange extends boolean">
  /* global TRange */
  import { slideFade } from "transitions/slide-fade";
  import { getRandomId } from "utils/random";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import { yymmdd } from "formatting/date-time";
  import type { DateRange } from "models/date-time";
  import Dialogue from "./dialogue.svelte";

  type TValue = TRange extends true ? DateRange : Date;

  export let range: TRange;
  export let value: TValue | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let id: string = getRandomId("date-picker");
  export let label: string | undefined = undefined;
  export let required = false;
  export let error: string | string[] | boolean = false;

  let expanded = false;
  let displayValue = getFormattedValue();

  $: value, (displayValue = getFormattedValue());
  $: placeholderShowing = placeholder && !value;
  $: displayError = error instanceof Array ? error.join(", ") : error;
  $: value, (error = false);

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

  function closeIfNotRange(): void {
    if (!range) {
      close();
    }
  }
</script>

<div class="date-picker" use:clickOutside={close}>
  {#if label}
    <label for={id} class="label">
      {label}
      {#if required}
        <span>*</span>
      {/if}
    </label>
  {/if}

  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <span class="header" on:click={toggle} on:keypress {id} class:error>
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
  </span>

  {#if typeof displayError === "string"}
    <span class="error-message" transition:slideFade={{ duration: 300 }}>{displayError}</span>
  {/if}

  {#if expanded}
    <Dialogue {range} bind:value on:select={closeIfNotRange} />
  {/if}
</div>

<style>
  .date-picker {
    --x-height: var(--height, 52px);
    --x-font-size: var(--font-size, 14px);
    --x-icon-padding: var(--icon-padding, 16px);
    --x-label-font-size: var(--label-font-size, 12px);
    --x-label-font-weight: var(--label-font-weight, 400);
    --x-label-font-family: var(--label-font-family, "Poppins");

    position: relative;
    display: inline-flex;
    flex-flow: column;
  }

  .label {
    margin-bottom: 8px;
    color: var(--color-main-neutral-900);
    font-weight: var(--x-label-font-weight);
    font-size: var(--x-label-font-size);
    font-family: var(--x-label-font-family);
    font-style: normal;
    letter-spacing: 0.5px;
  }

  .label > span {
    color: var(--color-main-primary-500);
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
    transition: border 150ms ease;
  }

  .header.error {
    border-color: #fe4e4e;
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

  .error-message {
    margin-top: 8px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
