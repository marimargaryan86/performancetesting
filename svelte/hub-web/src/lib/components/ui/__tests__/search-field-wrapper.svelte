<script lang="ts">
  // This wrapper is needed for testing two-way data binding:
  // https://testing-library.com/docs/svelte-testing-library/example/#two-way-data-binding
  import { writable, type Writable } from "svelte/store";
  import type { ComponentProps } from "svelte";
  import SearchField from "../search-field.svelte";

  interface $$Props extends Omit<ComponentProps<SearchField>, "value" | "clearValue"> {
    value: Writable<string | undefined>;
    clearValue: Writable<string | undefined>;
  }

  export let value: Writable<string | undefined> | undefined = writable(undefined);
  export let clearValue: Writable<string | undefined> | undefined = writable(undefined);
</script>

<SearchField {...$$props} bind:value={$value} bind:clearValue={$clearValue} />
