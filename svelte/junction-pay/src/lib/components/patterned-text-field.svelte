<script lang="ts">
  import TextField, { type InputEvent } from "./text-field.svelte";

  export let id: string | undefined = undefined;
  export let pattern: string;
  export let value: string | null | undefined = "";
  export let error: boolean | string | undefined = undefined;

  function getDigits(value: string): number[] {
    return (value.match(/\d/g) ?? []).map((digit) => parseInt(digit, 10));
  }

  function formatDigits(digits: number[]): string {
    let value = "";
    let idx = 0;

    for (const digit of digits) {
      while (idx < pattern.length && isNaN(parseInt(pattern[idx], 10))) {
        value += pattern[idx];
        idx++;
      }

      value += digit;
      idx++;
    }

    return value;
  }

  function formatInput(ev: CustomEvent<InputEvent>): void {
    const target = ev.detail.currentTarget;

    let start = target.selectionStart ?? 0;
    start = formatDigits(getDigits(target.value.substring(0, start))).length;

    target.value = value = formatDigits(getDigits(target.value));

    target.setSelectionRange(start, start);
  }
</script>

<TextField
  {error}
  {id}
  maxLength={pattern.length}
  on:input={formatInput}
  {value}
  placeholder={pattern}
/>
