<script lang="ts" context="module">
  import ActivityIcon from "assets/icons/activity-icon.svelte";
  import BankAccountIcon from "assets/icons/bank-account-icon.svelte";
  import BeneficiaryIcon from "assets/icons/beneficiary-icon.svelte";
  import DashboardIcon from "assets/icons/dashboard-icon.svelte";
  import PaymentIcon from "assets/icons/payment-icon.svelte";
  import SettingsIcon from "assets/icons/settings-icon.svelte";
  import type { ComponentType } from "svelte";
  import { page } from "$app/stores";

  type LinkItem = {
    type: "link";
    id: string;
    url: string;
    label: string;
    icon: ComponentType;
  };

  type SubMenu = {
    type: "sub-menu";
    id: string;
    label: string;
    color: string;
    items: {
      url: string;
      label: string;
      icon: ComponentType;
    }[];
  };

  const menuItems: (LinkItem | SubMenu)[] = [
    {
      type: "link",
      id: "dashboard",
      url: "/",
      label: "Dashboard",
      icon: DashboardIcon,
    },
    {
      type: "sub-menu",
      id: "pay",
      label: "Pay",
      color: "var(--color-pay-500)",
      items: [
        {
          url: "/pay/activity",
          label: "Activity",
          icon: ActivityIcon,
        },
        {
          url: "/pay/accounts",
          label: "Accounts",
          icon: BankAccountIcon,
        },
        {
          url: "/pay/beneficiaries",
          label: "Beneficiaries",
          icon: BeneficiaryIcon,
        },
        {
          url: "/pay/payment",
          label: "Payment",
          icon: PaymentIcon,
        },
      ],
    },
    {
      type: "sub-menu",
      id: "go",
      label: "Go",
      color: "var(--color-go-500)",
      items: [
        {
          url: "/go/cabin-mapping",
          label: "Cabin mapping",
          icon: SettingsIcon,
        },
      ],
    },
  ];
</script>

<ul class="menu">
  {#each menuItems as menuItem}
    <li>
      {#if menuItem.type === "link"}
        <a href={menuItem.url} class:active={$page.url.pathname === "/"} title={menuItem.label}>
          <svelte:component this={menuItem.icon} /><span>{menuItem.label}</span>
        </a>
      {:else}
        <input
          type="checkbox"
          id="sub-menu-{menuItem.id}"
          checked={menuItem.items.map((item) => item.url).includes($page.url.pathname)}
        />

        <label for="sub-menu-{menuItem.id}" title={menuItem.label}>
          <strong class="dot" style:--color={menuItem.color} /><span>{menuItem.label}</span>
        </label>

        <ul style:--max-height="{menuItem.items.length * 40}px" class="sub-menu">
          {#each menuItem.items as item}
            <li>
              <a href={item.url} class:active={$page.url.pathname === item.url} title={item.label}>
                <svelte:component this={item.icon} /><span>{item.label}</span>
              </a>
            </li>
          {/each}
        </ul>
      {/if}
    </li>
  {/each}
</ul>

<style>
  .menu {
    user-select: none;
  }

  label {
    cursor: pointer;
  }

  .sub-menu {
    height: 0;
    overflow: hidden;
    opacity: 0;
    transition: height 300ms ease, opacity 300ms ease;
  }

  input:checked ~ .sub-menu {
    height: var(--max-height);
    opacity: 1;
  }

  ul a {
    color: var(--color-neutral-800);
    font-weight: 600;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 20px;
    letter-spacing: 0.1px;
    white-space: nowrap;
    text-decoration: none;
    border-radius: 4px;
  }

  ul a.active {
    font-weight: 700;
    background-color: rgb(0 0 0 / 0.08);
  }

  ul label {
    color: var(--color-neutral-600);
    font-weight: 700;
    font-size: 12px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 24px;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  ul a,
  ul label {
    display: grid;
    grid-template-columns: 29px 1fr;
    align-items: center;
    justify-content: flex-start;
    height: 40px;
  }

  ul a > :global(svg) {
    justify-self: center;
    width: 20px;
    height: 20px;
  }

  ul label > span::after {
    position: relative;
    display: block;
    width: 8px;
    height: 8px;
    border: var(--color-neutral-400) 0 solid;
    border-width: 2px 2px 0 0;
    transform: translateY(-4px) rotateZ(135deg);
    transition: transform 200ms ease;
    content: "";
  }

  input:checked ~ label > span::after {
    transform: rotateZ(-45deg);
  }

  ul a > span,
  ul label > span {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px 0 4px;
    transition: opacity 300ms ease;
  }

  .dot {
    display: block;
    justify-self: center;
    width: 8px;
    height: 8px;
    background-color: var(--color);
    border-radius: 50%;
  }

  input {
    display: none;
  }
</style>
