<script lang="ts" context="module">
  import type { ComponentType } from "svelte";

  interface MenuItem {
    type: "menu-item";
    url: string;
    label: string;
    icon: ComponentType;
  }

  interface SubMenu {
    type: "sub-menu";
    label: string;
    color: string;
    expanded: boolean;
    items: MenuItem[];
  }
</script>

<script lang="ts">
  import AccountsIcon from "components/icons/accounts-icon.svelte";
  import ActivityIcon from "components/icons/activity-icon.svelte";
  import BeneficiaryIcon from "components/icons/beneficiary-icon.svelte";
  import DashboardIcon from "components/icons/dashboard-icon.svelte";
  import PaymentIcon from "components/icons/payment-icon.svelte";
  import SettingsIcon from "components/icons/settings-icon.svelte";
  import { page } from "$app/stores";
  import { slide } from "svelte/transition";
  import ChevronIcon from "components/icons/chevron-icon.svelte";

  export let expanded: boolean;
  export let transitionTimeMs: number;

  let menuItems: (MenuItem | SubMenu)[] = [
    {
      type: "menu-item",
      url: "/",
      label: "Dashboard",
      icon: DashboardIcon,
    },
    {
      type: "sub-menu",
      label: "Pay",
      color: "#ff7d37",
      expanded: $page.url.pathname.startsWith("/pay"),
      items: [
        {
          type: "menu-item",
          url: "/pay/activity",
          label: "Activity",
          icon: ActivityIcon,
        },
        {
          type: "menu-item",
          url: "/pay/accounts",
          label: "Accounts",
          icon: AccountsIcon,
        },
        {
          type: "menu-item",
          url: "/pay/beneficiaries",
          label: "Beneficiaries",
          icon: BeneficiaryIcon,
        },
        {
          type: "menu-item",
          url: "/pay/payments",
          label: "Payments",
          icon: PaymentIcon,
        },
      ],
    },
    {
      type: "sub-menu",
      label: "Go",
      color: "#b881ff",
      expanded: $page.url.pathname.startsWith("/go"),
      items: [
        {
          type: "menu-item",
          url: "/go/cabin-mapping",
          label: "Cabin mapping",
          icon: SettingsIcon,
        },
      ],
    },
  ];

  function createToggleFunc(menuItem: SubMenu): () => void {
    return () => {
      menuItem.expanded = !menuItem.expanded;

      menuItems = [...menuItems];
    };
  }
</script>

<ul class="menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  {#each menuItems as item}
    <li>
      {#if item.type === "menu-item"}
        <a
          href={item.url}
          class:active={$page.url.pathname === item.url}
          title={expanded ? undefined : item.label}
        >
          <svelte:component this={item.icon} color="var(--color-primary-500)" />
          <span>{item.label}</span>
        </a>
      {:else}
        <button
          type="button"
          on:click={createToggleFunc(item)}
          title={expanded ? undefined : item.label}
        >
          <strong style:--dot-color={item.color} />
          <span>{item.label}</span>
          <ChevronIcon color="var(--color-neutral-400)" direction={item.expanded ? "up" : "down"} />
        </button>

        {#if item.expanded}
          <ul transition:slide|local={{ duration: 250 }}>
            {#each item.items as subItem}
              <li>
                <a
                  href={subItem.url}
                  class:active={$page.url.pathname.startsWith(subItem.url)}
                  title={expanded ? undefined : subItem.label}
                >
                  <svelte:component this={subItem.icon} color="var(--color-primary-500)" />
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
    color: var(--color-neutral-900);
    font-weight: 600;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    letter-spacing: 0.1px;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    border-radius: 4px;
    cursor: pointer;
  }

  button {
    color: var(--color-neutral-600);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  strong {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  strong::before {
    display: block;
    width: 8px;
    height: 8px;
    background-color: var(--dot-color);
    border-radius: 50%;
    content: "";
  }

  strong,
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

  .menu:not(.expanded) span {
    opacity: 0;
  }

  .active {
    font-weight: 700;
    background-color: rgb(0 0 0 / 0.08);
  }
</style>
