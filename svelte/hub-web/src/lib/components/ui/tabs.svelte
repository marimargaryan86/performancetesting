<script lang="ts" context="module">
  export interface Tab {
    url: string;
    label: string;
    exact?: boolean;
  }
</script>

<script lang="ts">
  import { page } from "$app/stores";

  export let items: Tab[];
</script>

<ul typography="title-medium" weight="bold" class="tabs">
  {#each items as item}
    {@const active = item.exact
      ? $page.url.pathname === item.url
      : $page.url.pathname.startsWith(item.url)}

    <li class="tab"><a href={item.url} class:active>{item.label}</a></li>
  {/each}
</ul>

<style>
  .tabs {
    display: flex;
    gap: 24px;
  }

  a {
    color: var(--color-main-neutral-600);
    text-decoration: none;
    transition: color 150ms ease;
  }

  a::after {
    display: block;
    width: 0;
    margin-top: 12px;
    border-bottom: var(--color-main-primary-400) 4px solid;
    transition: width 150ms ease;
    content: "";
  }

  a.active {
    color: var(--color-common-light-strong);
  }

  a.active::after {
    width: 16px;
  }
</style>
