<script lang="ts" context="module">
  import type { ComponentType, SvelteComponent } from "svelte";

  interface MenuItem {
    type: "menu-item";
    url: string;
    label: string;
    icon: ComponentType<SvelteComponent<{ color?: string }>>;
  }

  interface SubMenu {
    type: "sub-menu";
    label: string;
    expanded: boolean;
    items: MenuItem[];
  }
</script>

<script lang="ts">
  import AccountsIcon from "components/icons/accounts-icon.svelte";
  import ActivityIcon from "components/icons/activity-icon.svelte";
  import DashboardIcon from "components/icons/dashboard-icon.svelte";
  import TicketIcon from "components/icons/ticket-icon.svelte";
  import { page } from "$app/stores";
  import { slide } from "svelte/transition";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import BeneficiaryIcon from "components/icons/beneficiary-icon.svelte";
  import routeConfig from "routeConfig";
  import BookingsIcon from "components/icons/bookings-icon.svelte";

  export let expanded: boolean;
  export let transitionTimeMs: number;

  let menuItems: (MenuItem | SubMenu)[] = [
    {
      type: "menu-item",
      url: routeConfig.home,
      label: "Dashboard",
      icon: DashboardIcon,
    },
    {
      type: "sub-menu",
      label: "Trip Management",
      expanded: $page.url.pathname.startsWith(routeConfig.tripManagement.root),
      items: [
        {
          type: "menu-item",
          url: routeConfig.tripManagement.book.root,
          label: "Book",
          icon: TicketIcon,
        },
        {
          type: "menu-item",
          url: routeConfig.tripManagement.orders.root,
          label: "View orders",
          icon: BookingsIcon,
        },
      ],
    },
    {
      type: "sub-menu",
      label: "Pay",
      expanded: $page.url.pathname.startsWith(routeConfig.pay.root),
      items: [
        {
          type: "menu-item",
          url: routeConfig.pay.activity.root,
          label: "Activity",
          icon: ActivityIcon,
        },
        {
          type: "menu-item",
          url: routeConfig.pay.accounts.root,
          label: "Accounts",
          icon: AccountsIcon,
        },
        {
          type: "menu-item",
          url: routeConfig.pay.beneficiaries.root,
          label: "Beneficiaries",
          icon: BeneficiaryIcon,
        },
      ],
    },
    {
      type: "sub-menu",
      label: "Go",
      expanded: $page.url.pathname.startsWith(routeConfig.go.root),
      items: [
        {
          type: "menu-item",
          url: routeConfig.go.bookings.root,
          label: "Bookings",
          icon: BookingsIcon,
        },
      ],
    },
  ];

  function toggle(menuItem: SubMenu): void {
    menuItem.expanded = !menuItem.expanded;

    menuItems = [...menuItems];
  }
</script>

<ul class="menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  {#each menuItems as item}
    <li>
      {#if item.type === "menu-item"}
        {@const active = $page.url.pathname === item.url}
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
      {:else}
        <button
          class="typography body-small"
          type="button"
          title={expanded ? undefined : item.label}
          on:click={toggle.bind(toggle, item)}
        >
          <span>{item.label}</span>
          <ChevronIcon
            color="var(--color-main-neutral-400)"
            direction={item.expanded ? "up" : "down"}
          />
        </button>

        {#if item.expanded}
          <ul transition:slide={{ duration: 250 }}>
            {#each item.items as subItem}
              {@const active = $page.url.pathname.startsWith(subItem.url)}
              <li>
                <a
                  class="typography body-medium"
                  href={subItem.url}
                  class:active
                  title={expanded ? undefined : subItem.label}
                >
                  <svelte:component
                    this={subItem.icon}
                    color="var({active
                      ? '--color-main-primary-500'
                      : '--color-common-light-strong'})"
                  />
                  <span>{subItem.label}</span>
                </a>
              </li>
            {/each}
          </ul>
        {/if}
      {/if}
    </li>
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

  a,
  button {
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

  button {
    color: var(--color-common-light-soft);
    text-transform: uppercase;
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
