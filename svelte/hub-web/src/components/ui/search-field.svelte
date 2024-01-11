<script lang="ts">
  import TextField from "./text-field.svelte";
  import { getLocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";

  let placeholderExt: string | undefined = undefined;
  export { placeholderExt as placeholder };
  export let value = "";
  export let clearable = false;
  export let clearValue = "";

  const i18n = getLocaleData();

  let focused = false;

  $: placeholder = placeholderExt ?? $i18n.actions.search;
  $: expanded = Boolean(value.length || focused);

  function focus(): void {
    focused = true;
  }

  function blur(): void {
    focused = false;
  }
</script>

<TextField
  bind:value
  {placeholder}
  class="search-field {expanded ? 'expanded' : ''}"
  on:focus={focus}
  on:blur={blur}
  name="search"
  {clearable}
  {clearValue}
>
  <Icon variant="search" size="20px" slot="icon-before" color="var(--color-main-primary-500)" />
</TextField>

<style>
  :global(.text-field.search-field) {
    --border-color: transparent;
    --height: 40px;
    --icon-padding: 8px;

    width: 40px;
    cursor: pointer;
    transition: width 400ms ease;
  }

  :global(.text-field.search-field.expanded) {
    --border-color: unset;
    --icon-padding: unset;

    width: 235px;
    cursor: text;
  }

  :global(.text-field.search-field:not(.expanded) input::placeholder) {
    opacity: 0;
  }
</style>
