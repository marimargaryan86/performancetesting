<script lang="ts" context="module">
  /* TODO: Impl. */
  export type Direction = "ascending" | "descending";
</script>

<script lang="ts">
  import ChevronIcon from "$lib/icons/chevron-icon.svelte";

  export let direction: Direction | undefined = undefined;

  let title: string;

  $: {
    switch (direction) {
      case "ascending":
        title = "Sort descending";
        break;
      case "descending":
      case undefined:
        title = "Sort ascending";
        break;
    }
  }

  function change(): void {
    switch (direction) {
      case "ascending":
        direction = "descending";
        break;
      case "descending":
      case undefined:
        direction = "ascending";
        break;
    }
  }
</script>

<button
  {title}
  class="sorter"
  class:ascending={direction === "ascending"}
  class:descending={direction === "descending"}
  class:inactive={!direction}
  on:click={change}
>
  <ChevronIcon />
</button>

<style>
  .sorter {
    background-color: transparent;
    border: transparent 0px solid;
    padding: 0;
    margin: 0;
    stroke: var(--color-teal-dark);
    cursor: pointer;
  }

  .sorter.inactive {
    stroke: var(--color-teal-lighter);
  }

  .sorter > :global(svg) {
    vertical-align: top;
    transition: transform 150ms ease;
  }

  .sorter.descending > :global(svg) {
    transform: rotateZ(180deg);
  }
</style>
