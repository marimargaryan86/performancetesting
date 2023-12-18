<script lang="ts" generics="TSortGroup">
  /* global TSortGroup */
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { DirectionY } from "models/spatial";

  export let textAlign: "left" | "right" = "left";
  export let sortDirection: DirectionY | undefined = undefined;
  export let sortValue: Readonly<TSortGroup> | undefined = undefined;
  export let sortGroup: TSortGroup | undefined = undefined;

  $: sortable = Boolean(sortGroup && sortValue && sortDirection);
  $: sortingActive = sortValue !== undefined && sortGroup !== undefined && sortValue === sortGroup;

  function sort(): void {
    if (sortingActive) {
      sortDirection = sortDirection === "down" ? "up" : "down";
    } else {
      sortDirection = "down";
    }

    sortGroup = sortValue;
  }
</script>

<th class:sortable on:click={sortable ? sort : undefined} style:text-align={textAlign}>
  <slot />

  {#if sortable}
    <ChevronIcon
      variant="filled"
      color="var(--color-common-light-soft)"
      direction={sortingActive ? sortDirection : "down"}
    />
  {/if}
</th>

<style>
  th {
    position: sticky;
    top: 0;
    z-index: calc(var(--z-index-ui-dialog) - 1);
    gap: 8px;
    padding: 16px;
    white-space: nowrap;
    text-align: left;
    background-color: var(--color-main-primary-50);
  }

  th.sortable {
    cursor: pointer;
  }

  th::after {
    position: absolute;
    bottom: 0;
    left: 0;
    display: block;
    width: 100%;
    border-bottom: var(--color-main-neutral-50) 1px solid;
    content: "";
  }

  th > :global(*) {
    vertical-align: top;
  }
</style>
