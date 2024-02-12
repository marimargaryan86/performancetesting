<script lang="ts">
  import type { ComponentEvents } from "svelte";
  import TextField from "./text-field.svelte";
  import {
    validateAndGetDate,
    validateDay,
    validateMonth,
    validateYear,
  } from "$lib/utils/date-time";

  export let placeholder = "DD/MM/YYYY";
  export let label: string | undefined = undefined;
  export let value: Date | undefined = undefined;
  export let error: string | string[] | undefined = undefined;
  export let required = false;

  let currentErrors: string[];
  let valueStr = value?.toLocaleDateString("en-GB") ?? "";

  function update(event: ComponentEvents<TextField>["input"]): void {
    const erase = event.detail.value.length < valueStr.length;
    const nextValue = event.detail.value.replace(/\//g, "");

    if (erase && valueStr.endsWith("/")) {
      valueStr = valueStr.substring(0, valueStr.length - 2);

      return;
    }

    valueStr = [nextValue.substring(0, 2), nextValue.substring(2, 4), nextValue.substring(4, 8)]
      .filter((p) => p.length)
      .join("/");

    if (valueStr.length === 2 || valueStr.length === 5) {
      valueStr += "/";
    }
  }

  $: currentErrors = [];

  $: if (valueStr) {
    value = validateAndGetDate(valueStr);
  }

  /**
   * Validates and populates errors based off the raw string value.
   */
  $: if (valueStr.length === 10) {
    const day = valueStr.slice(0, 2);
    const month = valueStr.slice(3, 5);
    const year = valueStr.slice(6, 10);

    const nextErrors = [validateDay(day), validateMonth(month), validateYear(year)].reduce(
      (acc: string[], [isValid, errorStr]) => {
        if (!isValid) {
          acc.push(errorStr as string);
        }

        return acc;
      },
      [],
    );

    currentErrors = nextErrors;
  }

  $: if (valueStr.length < 10) {
    currentErrors = [];
  }

  $: if (currentErrors.length > 0) {
    error = currentErrors;
  }
</script>

<TextField
  value={valueStr}
  {placeholder}
  {label}
  {required}
  {error}
  maxlength={10}
  on:input={update}
/>
