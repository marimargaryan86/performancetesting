<script lang="ts">
  import Tabs from "$lib/components/ui/tabs.svelte";
  import BreadCrumbs from "./bread-crumbs.svelte";
  import FilterIcon from "$lib/components/icons/filter-icon.svelte";
  import { slideFade } from "$lib/transitions/slide-fade";
  import SearchField from "$lib/components/ui/search-field.svelte";
  import type { BreadCrumb, Tab } from "$lib/models/ui";

  export let breadCrumbs: BreadCrumb[] | undefined = undefined;
  export let pageTitle = "";
  export let pageSubTitle: string | undefined = undefined;
  export let tabs: Tab[] | undefined = undefined;
  export let filtersActive = false;
  export let searchQuery: string | undefined = undefined;

  let showFilters = false;

  const hasFilters = Boolean($$slots.filters);

  $: hasNavigation = $$slots["navigation-left"] || $$slots["navigation-right"];
  $: hasFiltersOrTabs = Boolean(hasFilters || tabs);
  $: hasActions = hasFilters || searchQuery !== undefined || $$slots.actions;

  function toggleFilters(): void {
    showFilters = !showFilters;
  }
</script>

{#if breadCrumbs}
  <BreadCrumbs items={breadCrumbs} />
{/if}

<div class="header" class:after-breadcrumbs={breadCrumbs}>
  <h1>
    <span typography="headline-medium" weight="bold">
      <slot name="page-title">
        {pageTitle}
      </slot>
    </span>

    {#if $$slots["page-sub-title"] || pageSubTitle !== undefined}
      <em typography="body-small">
        <slot name="page-sub-title">
          {pageSubTitle}
        </slot>
      </em>
    {/if}
  </h1>

  {#if hasActions}
    <div class="actions">
      {#if searchQuery !== undefined}
        <SearchField bind:value={searchQuery} clearable />
      {/if}

      {#if hasFilters}
        <button on:click={toggleFilters}>
          <FilterIcon color="var(--color-main-primary-500)" active={filtersActive} />
        </button>
      {/if}

      <slot name="actions" />
    </div>
  {/if}
</div>

<slot name="steps" />

{#if hasFiltersOrTabs}
  <div class="filters-and-tabs">
    {#if showFilters}
      <div class="filters" transition:slideFade={{ duration: 250 }} class:tabs-after={tabs}>
        <slot name="filters" />
      </div>
    {/if}

    {#if tabs}
      <div class="tabs">
        <Tabs items={tabs} />
      </div>
    {/if}
  </div>
{/if}

{#if $$slots["content-before"]}
  <slot name="content-before" />
{/if}

<div class="content">
  <slot />
</div>

{#if hasNavigation}
  <div class="navigation">
    <slot name="navigation-left" />
    <span />
    <slot name="navigation-right" />
  </div>
{/if}

<style>
  .header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 16px 24px;
    color: var(--color-main-neutral-800);
  }

  .header.after-breadcrumbs {
    padding: 8px 24px 24px;
  }

  h1 {
    display: flex;
    flex-flow: column;
    gap: 8px;
  }

  h1 > em {
    color: var(--color-main-neutral-700);
  }

  .actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .actions > button {
    height: 40px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .filters-and-tabs {
    padding: 0 24px;
    background-color: var(--color-main-primary-50);
  }

  .filters {
    --height: 42px;

    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(276px, 1fr));
    gap: 16px 16px;
    align-items: flex-end;
    margin: 16px;
  }

  .tabs {
    padding-top: 16px;
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-color: #fafafa;
  }

  .navigation {
    display: flex;
    gap: 16px;
    padding: 16px 24px;
  }

  .navigation > span {
    flex-grow: 1;
  }
</style>
