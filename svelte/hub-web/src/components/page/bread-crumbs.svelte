<script lang="ts" context="module">
  export interface BreadCrumb {
    url: string;
    label: string;
  }
</script>

<script lang="ts">
  import ChevronIcon from "~/components/icons/chevron-icon.svelte";

  export let items: BreadCrumb[];
</script>

<ul class="bread-crumbs">
  {#each items as item, idx}
    <li typography="body-small" class="bread-crumb">
      {#if idx !== items.length - 1}
        <a href={item.url}>{item.label}</a>

        <ChevronIcon size="10px" color="var(--color-main-neutral-700)" />
      {:else}
        <span>{item.label}</span>
      {/if}
    </li>
  {/each}
</ul>

<style>
  .bread-crumbs {
    display: flex;
    gap: 4px;
    padding: 16px 24px;
  }

  .bread-crumb {
    display: flex;
    gap: 4px;
    align-items: center;
    color: var(--color-main-neutral-700);
  }

  .bread-crumb > a {
    color: var(--color-main-primary-500);
    text-decoration: none;
  }
</style>
