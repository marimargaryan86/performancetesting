<script lang="ts">
  // This wrapper is needed for testing two-way data binding:
  // https://testing-library.com/docs/svelte-testing-library/example/#two-way-data-binding
  import type { Writable } from "svelte/store";
  import type { ComponentProps } from "svelte";
  import DateTextField from "../date-text-field.svelte";

  interface $$Props extends Omit<ComponentProps<DateTextField>, "value"> {
    value: Writable<Date | undefined>;
  }

  export let value: Writable<Date | undefined>;
</script>

<DateTextField {...$$props} bind:value={$value} />
