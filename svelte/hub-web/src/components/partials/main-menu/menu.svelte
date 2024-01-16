<script lang="ts">
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import { permitted, type Action, getUser } from "utils/permissions";
  import { getLocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";

  export let expanded: boolean;
  export let transitionTimeMs: number;

  const user = getUser();
  const i18n = getLocaleData();

  let menuItems: {
    url: string;
    label: string;
    icon: Icon["$$prop_def"]["variant"];
    exact?: boolean;
    permission?: Action;
  }[];

  $: menuItems = [
    {
      url: routeConfig.routes.tripManagement.routes.book.root,
      label: $i18n.pages.tripManagement.pages.book.title,
      icon: "ticket",
    },
    {
      url: routeConfig.routes.tripManagement.routes.orders.root,
      label: $i18n.pages.tripManagement.pages.orders.title,
      icon: "bookings",
      permission: "journey.view",
    },
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $i18n.pages.pay.pages.activity.title,
      icon: "activity",
      permission: "transaction.view",
    },
    {
      url: routeConfig.routes.pay.routes.bills.root,
      label: $i18n.pages.pay.pages.bills.title,
      icon: "bill",
      permission: "*",
    },
  ];
</script>

<ul class="menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  {#each menuItems as item}
    {#if !item.permission || permitted($user, item.permission)}
      {@const active = item.exact
        ? $page.url.pathname === item.url
        : $page.url.pathname.startsWith(item.url)}
      <li>
        <a
          href={item.url}
          typography="body-medium"
          class:active
          title={expanded ? undefined : item.label}
        >
          <Icon
            variant={item.icon}
            color="var({active ? '--color-main-primary-500' : '--color-common-light-strong'})"
            size="20px"
          />
          <span>{item.label}</span>
        </a>
      </li>
    {/if}
  {/each}
</ul>

<style>
  .menu {
    width: 100%;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 2px;
  }

  a {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
    padding: 10px 8px;
    overflow: hidden;
    color: var(--color-common-light-medium);
    text-decoration: none;
    background-color: transparent;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
  }

  a > :global(.icon) {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
  }

  span {
    flex-grow: 1;
    white-space: nowrap;
    text-align: left;
    transition: opacity var(--transition-time) ease;
  }

  .menu:not(.expanded) a > span {
    opacity: 0;
  }

  .active {
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-green);
  }
</style>
