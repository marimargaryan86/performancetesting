<script lang="ts" generics="TRange extends boolean">
  /* global TRange */
  import { getRandomId } from "utils/random";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { clickOutside } from "directives/click-outside";
  import type { DateRange } from "models/date-time";
  import Dialogue from "./dialogue.svelte";
  import TextField from "../text-field.svelte";

  type TValue = TRange extends true ? DateRange : Date;

  export let range: TRange;
  export let value: TValue | undefined = undefined;
  export let placeholder: string | undefined = undefined;
  export let id: string = getRandomId("date-picker");
  export let label: string | undefined = undefined;
  export let required = false;
  export let error: string | string[] | boolean = false;
  export let span: DateRange | undefined = undefined;

  let expanded = false;

  $: displayValue = getFormattedValue(value);
  $: value, (error = false);

  function getFormattedValue(nextValue: TValue | undefined): string | undefined {
    if (!nextValue) {
      return undefined;
    }

    if (nextValue instanceof Date) {
      return nextValue.toLocaleDateString("en-GB");
    }

    if (nextValue.from && nextValue.to) {
      return `${nextValue.from.toLocaleDateString("en-GB")} - ${nextValue.to.toLocaleDateString(
        "en-GB",
      )}`;
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

  function clear(): void {
    value = undefined;
  }

  function closeIfNotRange(): void {
    if (!range) {
      close();
    }
  }
</script>

<div class="date-picker" use:clickOutside={close} class:has-value={value}>
  <TextField
    {id}
    {label}
    {required}
    readonly
    {placeholder}
    value={displayValue}
    {error}
    clearable
    on:click={toggle}
    on:clear={clear}
  >
    <ChevronIcon
      direction={expanded ? "up" : "down"}
      color="var(--color-common-light-strong)"
      slot="icon-after"
    />
  </TextField>

  {#if expanded}
    <Dialogue {range} {span} bind:value on:select={closeIfNotRange} />
  {/if}
</div>

<style>
  .date-picker {
    position: relative;
    display: inline-flex;
    flex-flow: column;
  }

  .date-picker > :global(.text-field) {
    cursor: pointer;
  }

  .date-picker.has-value > :global(.text-field .chevron-icon) {
    display: none;
  }
</style>
