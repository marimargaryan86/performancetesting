<script lang="ts" generics="TValue">
  // This wrapper is needed for testing two-way data binding:
  // https://testing-library.com/docs/svelte-testing-library/example/#two-way-data-binding
  /* global TValue */
  import type { Writable } from "svelte/store";
  import type { ComponentProps } from "svelte";
  import AutocompleteField from "../autocomplete-field.svelte";

  interface $$Props extends Omit<ComponentProps<AutocompleteField<TValue>>, "value"> {
    value: Writable<TValue | undefined>;
  }

  export let value: Writable<TValue | undefined>;
</script>

<AutocompleteField {...$$props} bind:value={$value} />
