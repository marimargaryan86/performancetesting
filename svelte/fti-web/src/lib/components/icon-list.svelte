<script context="module" lang="ts">
  export type IconListItemConfig = { iconType: IconTypes | AmenityIcons; label: string };
  export type IconListConfig = Array<IconListItemConfig>;
</script>

<script lang="ts">
  import type { AmenityIcons, IconTypes } from "$lib/models/common";
  import Icon from "./icon.svelte";

  export let iconList: IconListConfig = [];
  export let formatter: ((label: string) => string) | undefined = undefined;
  export let variant: "row" | "column" = "column";
</script>

<!--
  * Given an `IconListConfig`, returns a list with icons and labels.
  *
  * - Supports "row" and "column" variants. When configuring a "column",
  *   specify custom `--num-columns={numColumns}` HTML attribute.
  * - Supports a label `formatter` function to transform strings.
  * -->
{#if iconList.length}
  <ul class:column={variant === "column"} class:row={variant === "row"}>
    {#each iconList as iconListItem}
      <li>
        <p>
          <Icon size="12px" color="#00a8cd" variant={iconListItem.iconType} />
          {formatter ? formatter(iconListItem.label) : iconListItem.label}
        </p>
      </li>
    {/each}
  </ul>
{/if}

<style>
  p,
  ul,
  li {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 12px;
    margin: 0;
    padding: 0;
  }

  ul.column {
    columns: var(--num-columns, 2);
    -webkit-columns: var(--num-columns, 2);
    -moz-columns: var(--num-columns, 2);
  }

  ul.column > li {
    padding-bottom: 8px;
  }

  ul.row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
  }

  li {
    list-style: none;
  }
</style>
