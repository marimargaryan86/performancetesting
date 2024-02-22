<script lang="ts" context="module">
  const links = [
    {
      type: "rail",
      url: routeConfig.routes.tripManagement.routes.book.routes.rail.root,
    },
    {
      type: "car",
      url: routeConfig.routes.tripManagement.routes.book.routes.car.root,
    },
  ] as const satisfies { type: TransportType; url: string }[];
</script>

<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import type { TransportType } from "~/integration/common/schemas";
  import type { SearchType } from "~/params/offer_search_type";

  const t = getTranslator();

  export let active: SearchType;
</script>

<div class="search-tabs" typography="title-small" weight="bold">
  {#each links as link}
    <a href={link.url} class:active={active === link.type}>
      {$t(`transportTypes.${link.type}`)}
    </a>
  {/each}
</div>

<style>
  .search-tabs {
    display: flex;
    border-bottom: var(--color-common-line-soft) 1px solid;
  }

  a {
    margin-bottom: -1px;
    padding: 8px 16px;
    color: var(--color-common-light-strong);
    text-decoration: none;
    border-bottom: transparent 2px solid;
  }

  a.active {
    color: var(--color-main-primary-500);
    border-bottom-color: var(--color-main-primary-500);
  }
</style>
