<script lang="ts">
  import { createDatePicker, melt } from "@melt-ui/svelte";
  import { getLocale } from "i18n/index";
  import { slideFade } from "transitions/slide-fade";
  import {
    toCalendarDateTime,
    toCalendarDate,
    now,
    fromDate,
    getLocalTimeZone,
    type DateValue,
    CalendarDateTime,
  } from "@internationalized/date";

  import Calendar from "./calendar.svelte";
  import Icon from "components/icons/icon.svelte";
  import { scale } from "svelte/transition";
  import TimePicker from "./time-picker.svelte";
  import { writable } from "svelte/store";

  let externalValue: Date | undefined;
  export { externalValue as value };
  export let required = false;
  let externalLabel: string | undefined = undefined;
  export { externalLabel as label };
  export let error: string | string[] | boolean = false;
  let externalMin: Date | undefined = undefined;
  export { externalMin as min };
  $: min = externalMin ? toCalendarDateTime(fromDate(externalMin, timeZone)) : undefined;
  export let includeTime = false;

  let timePicker: TimePicker | undefined;

  const timeZone = getLocalTimeZone();

  const value = writable<DateValue | undefined>(getValue());
  $: externalValue, ($value = getValue());
  $: $value, timePicker?.scrollToSelected("smooth");
  $: updateExternalValue($value);

  function getValue(): DateValue | undefined {
    const func = includeTime ? toCalendarDateTime : toCalendarDate;

    return externalValue ? func(fromDate(externalValue, timeZone)) : undefined;
  }

  function getPlaceholder(): DateValue {
    return includeTime
      ? toCalendarDateTime(now(timeZone)).set({ minute: 0, second: 0 })
      : toCalendarDate(now(timeZone));
  }

  function updateExternalValue(nextValue?: DateValue): void {
    externalValue = nextValue ? new Date(nextValue.toString()) : undefined;
  }

  const locale = getLocale();
  const {
    options,
    elements: { content, field, label, segment, trigger, ...calendarElements },
    states: { segmentContents, open, ...calendarStates },
    helpers: { isDateDisabled, isDateUnavailable, isDateSelected },
  } = createDatePicker({
    forceVisible: true,
    locale: $locale,
    required,
    defaultPlaceholder: getPlaceholder(),
    value,
    weekdayFormat: "short",
    onValueChange({ curr, next }) {
      if (next instanceof CalendarDateTime) {
        return next.set({ minute: 0, second: 0 });
      }

      return curr instanceof CalendarDateTime
        ? next?.set({ hour: curr?.hour, minute: 0, second: 0 })
        : next;
    },
    minValue: min,
  });

  $: includeTime, options.defaultPlaceholder?.set(getPlaceholder());
  $: options.minValue.set(min);
  $: options.locale.set($locale);
  $: options.required.set(required);
  $: $value, (error = false);
  $: displayError = error instanceof Array ? error.join(", ") : error;
</script>

<div class="date-picker">
  {#if externalLabel}
    <span use:melt={$label} typography="body-medium" weight="bold">
      {externalLabel}
      {#if required}<span class="required">*</span>{/if}
    </span>
  {/if}

  <div use:melt={$field} class="input" typography="body-large" class:error>
    <div class="segments">
      {#each $segmentContents as seg, idx (idx)}
        <div use:melt={$segment(seg.part)} class="segment">
          {seg.value}
        </div>
      {/each}
    </div>

    <button use:melt={$trigger} type="button" class="dialog-toggle">
      <Icon variant="calendar" color="var(--color-main-primary-700)" />
    </button>
  </div>

  {#if $open}
    <div class="popover" use:melt={$content} transition:scale={{ duration: 200, start: 0.8 }}>
      {#if externalLabel}
        <div typography="headline-medium" class="title">{externalLabel}</div>
      {/if}

      <Calendar
        elements={calendarElements}
        states={calendarStates}
        helpers={{ isDateDisabled, isDateUnavailable, isDateSelected }}
      />

      {#if includeTime && (!$value || $value instanceof CalendarDateTime)}
        <TimePicker
          bind:this={timePicker}
          bind:value={$value}
          {min}
          isDateDisabled={$isDateDisabled}
        />
      {/if}
    </div>
  {/if}

  {#if typeof displayError === "string"}
    <span class="error-message" transition:slideFade={{ duration: 300 }}>{displayError}</span>
  {/if}
</div>

<style>
  .date-picker {
    --x-height: var(--height, 52px);
    --x-icon-size: var(--icon-size, 24px);

    display: inline-flex;
    flex-flow: column;
    gap: 2px;
  }

  .input {
    display: flex;
    justify-content: space-between;
    height: var(--x-height);
    padding: 0 16px;
    background: var(--color-common-background-light-main);
    border: var(--color-common-line-medium) 1px solid;
    border-radius: 8px;
    transition: border 150ms ease;
  }

  .input:focus-within {
    border-color: var(--color-common-line-strong);
  }

  .input.error {
    border-color: #fe4e4e;
  }

  .segments {
    display: flex;
    gap: 1px;
    align-items: center;
  }

  .segment {
    display: flex;
    align-items: center;
    border-radius: 4px;
  }

  .segment:focus {
    background-color: var(--color-semantic-warning-200);
    outline: 0;
  }

  .required {
    color: var(--color-main-primary-500);
  }

  .dialog-toggle {
    align-self: center;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .dialog-toggle > :global(.icon) {
    --size: var(--x-icon-size, 24px);
  }

  .popover {
    z-index: var(--z-index-ui-dialog);
    width: 384px;
    padding: 32px 24px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 0 0 20px 4px rgb(0 0 0 / 0.04);
    transform-origin: center 0;
  }

  .popover > .title {
    padding: 0 0 24px;
    border-bottom: var(--color-common-line-soft) 1px solid;
  }

  .error-message {
    margin-top: 6px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
