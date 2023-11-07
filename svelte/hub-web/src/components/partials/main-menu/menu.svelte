<script lang="ts" context="module">
  import type { ComponentType, SvelteComponent } from "svelte";

  interface MenuItem {
    url: string;
    label: string;
    icon: ComponentType<SvelteComponent<{ color?: string }>>;
    exact?: boolean;
    permissions?: {
      module: PermissionModule;
      action?: PermissionAction;
    };
  }

  const menuItems: MenuItem[] = [
    {
      url: routeConfig.routes.tripManagement.routes.book.root,
      label: "Book",
      icon: TicketIcon,
    },
    {
      url: routeConfig.routes.tripManagement.routes.orders.root,
      label: "View orders",
      icon: BookingsIcon,
      permissions: {
        module: "journey",
        action: "view",
      },
    },
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: "Activity",
      icon: ActivityIcon,
      permissions: {
        module: "transaction",
        action: "*",
      },
    },
    {
      url: routeConfig.routes.pay.routes.bills.root,
      label: "Bills",
      icon: BillIcon,
      permissions: {
        module: "*",
      },
    },
  ];
</script>

<script lang="ts">
  import ActivityIcon from "components/icons/activity-icon.svelte";
  import TicketIcon from "components/icons/ticket-icon.svelte";
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import BookingsIcon from "components/icons/bookings-icon.svelte";
  import BillIcon from "components/icons/bill-icon.svelte";
  import { type PermissionAction, type PermissionModule, permitted } from "utils/permissions";
  import userStore from "stores/user-store";

  export let expanded: boolean;
  export let transitionTimeMs: number;

  $: user = $userStore;
</script>

<ul class="menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  {#each menuItems as item}
    {#if !item.permissions || permitted(user, item.permissions.module, item.permissions.action)}
      {@const active = item.exact
        ? $page.url.pathname === item.url
        : $page.url.pathname.startsWith(item.url)}
      <li>
        <a
          href={item.url}
          class="typography body-medium"
          class:active
          title={expanded ? undefined : item.label}
        >
          <svelte:component
            this={item.icon}
            color="var({active ? '--color-main-primary-500' : '--color-common-light-strong'})"
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

  a > :global(svg) {
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
