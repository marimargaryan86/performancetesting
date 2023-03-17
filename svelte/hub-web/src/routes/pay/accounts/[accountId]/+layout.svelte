<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import type { LayoutData } from "./$types";

  export let data: LayoutData;
</script>

<h1 class="layout page-header">{data.account.name}</h1>

<ul class="bread-crumbs">
  {#each data.breadCrumbs as item, idx}
    {#if idx !== 0}
      <ChevronIcon color="var(--color-neutral-700)" size="12px" />
    {/if}

    <li>
      {#if idx !== data.breadCrumbs.length - 1}
        <a href={item.url}>{item.label}</a>
      {:else}
        <span>{item.label}</span>
      {/if}
    </li>
  {/each}
</ul>

<div class="layout content-box">
  <slot />
</div>

<style>
  .layout.page-header {
    letter-spacing: 1px;
    text-transform: none;
  }

  .bread-crumbs {
    display: flex;
    gap: 4px;
    align-items: center;
    margin-bottom: 16px;
    color: #66686b;
    font-weight: 600;
    font-size: 12px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }

  .bread-crumbs > li > a {
    color: var(--color-primary-500);
  }

  .layout.content-box {
    padding: 24px;
  }
</style>
