<script lang="ts">
  import SearchIcon from "components/icons/search-icon.svelte";
  import TextField from "./text-field.svelte";

  export let value = "";
  export let placeholder = "Search";

  let focused = false;

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
>
  <SearchIcon slot="icon-before" color="var(--color-main-primary-500)" />
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

  :global(.text-field.search-field input::placeholder) {
    transition: opacity 200ms ease;
  }

  :global(.text-field.search-field:not(.expanded) input::placeholder) {
    opacity: 0;
  }
</style>
