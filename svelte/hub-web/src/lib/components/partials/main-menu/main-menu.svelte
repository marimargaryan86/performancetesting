<script lang="ts">
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import Account from "./account.svelte";
  import { page } from "$app/stores";
  import routeConfig from "$lib/route-config";
  import integrationInstancesClient from "~/integration-instances-client";
  import { getTranslator } from "$lib/i18n";
  import { goto } from "$app/navigation";
  import Icon from "$lib/components/icons/icon.svelte";
  import JunctionLogo from "./junction-logo.svelte";
  import { type Action, getUser, permitted } from "$lib/utils/permissions";
  import LanguageSelect from "./language-select.svelte";
  import type { ComponentProps } from "svelte";
  import { slide } from "svelte/transition";

  let compact = false;

  const user = getUser();
  const t = getTranslator();
  const transitionTimeMs = 250;

  function toggleSidebar(): void {
    compact = !compact;
  }

  async function logout(): Promise<void> {
    await integrationInstancesClient.ory.auth.logout();
    await goto(routeConfig.routes.login.root, { invalidateAll: true });
  }

  type MenuItemSpacer = { type: "spacer" };

  type MenuItemLink = {
    type: "link";
    url: string;
    label: string;
    icon: ComponentProps<Icon>["variant"];
    activeMatcher?: (pathname: string) => boolean;
    permission?: Action;
  };

  type MenuItemParent = {
    type: "parent";
    url?: string;
    label: string;
    icon: ComponentProps<Icon>["variant"];
    activeMatcher?: (pathname: string) => boolean;
    permission?: Action;
    children: MenuItem[];
    expanded: boolean;
  };

  type MenuItem = MenuItemSpacer | MenuItemLink | MenuItemParent;

  let menuItems: MenuItem[];

  $: menuItems = [
    {
      type: "link",
      url: routeConfig.routes.tripManagement.routes.book.routes.train.root,
      activeMatcher: (pathname): boolean =>
        pathname.startsWith(routeConfig.routes.tripManagement.routes.book.root),
      label: $t("pages.tripManagement.pages.book.title"),
      icon: "ticket",
    },
    {
      type: "link",
      url: routeConfig.routes.tripManagement.routes.orders.root,
      label: $t("pages.tripManagement.pages.orders.title"),
      icon: "bookings",
      permission: "journey.view",
    },
    {
      type: "link",
      url: routeConfig.routes.pay.routes.activity.root,
      label: $t("pages.pay.pages.activity.title"),
      icon: "activity",
      permission: "transaction.view",
    },
    {
      type: "link",
      url: routeConfig.routes.pay.routes.bills.root,
      label: $t("pages.pay.pages.bills.title"),
      icon: "bill",
      permission: "*",
    },
    {
      type: "parent",
      label: $t("pages.adminControls.title"),
      icon: "password",
      permission: "users.view",
      children: [
        {
          type: "link",
          icon: "user",
          url: routeConfig.routes.adminControls.routes.users.root,
          label: $t("pages.adminControls.pages.users.title"),
          permission: "users.view",
          activeMatcher: (pathname): boolean =>
            pathname.startsWith(routeConfig.routes.adminControls.routes.users.root),
        },
      ],
      expanded: false,
    },
    {
      type: "spacer",
    },
    {
      type: "link",
      url: routeConfig.routes.knowledgeHub.root,
      label: $t("pages.knowledgeHub.title"),
      icon: "knowledge",
    },
    {
      type: "link",
      url: routeConfig.routes.help.routes.customerService.root,
      label: $t("actions.reportAnIssue"),
      icon: "bug",
    },
    {
      type: "link",
      url: routeConfig.routes.help.routes.privacyPolicy.root,
      label: $t("words.help"),
      icon: "information",
      activeMatcher: (pathname): boolean =>
        pathname.startsWith(routeConfig.routes.help.root) &&
        pathname !== routeConfig.routes.help.routes.customerService.root,
    },
  ];

  function toggleSubmenu(item: MenuItemParent): void {
    item.expanded = !item.expanded;
    // Create a new array (needed to detect change to trigger reactivity)
    menuItems = [...menuItems];
  }
</script>

<div
  class="main-menu"
  class:compact
  style:--transition-time="{transitionTimeMs}ms"
  style:width={compact ? "69px" : "240px"}
>
  <a href="/" class="home">
    <JunctionLogo {compact} {transitionTimeMs} />
  </a>

  <ul>
    {#each menuItems as item}
      <!-- Handle Spacer -->
      {#if item.type === "spacer"}
        <li class="spacer" />
      {:else}
        <!-- Handle parent navbar items with no children (link to routes) -->
        {#if !item.permission || permitted($user, item.permission)}
          {#if item.type === "link"}
            {@const active = item.activeMatcher
              ? item.activeMatcher($page.url.pathname)
              : $page.url.pathname.startsWith(item.url)}
            <li>
              <a
                href={item.url}
                typography="body-medium"
                class:active
                class="item"
                title={item.label}
              >
                <Icon
                  variant={item.icon}
                  color="var({active ? '--color-main-primary-500' : '--color-common-light-strong'})"
                  size="20px"
                />
                <span>{item.label}</span>
              </a>
            </li>
          {:else if item.type === "parent" && item.url}
            <!-- Handle parent items that link to routes AND have children -->
            {@const active =
              item.url && item.activeMatcher
                ? item.activeMatcher($page.url.pathname)
                : $page.url.pathname.startsWith(item.url)}
            <li>
              <a
                href={item.url}
                typography="body-medium"
                class:active
                class="item"
                title={item.label}
                on:click={toggleSubmenu.bind(toggleSubmenu, item)}
              >
                <Icon
                  variant={item.icon}
                  color="var(--{active ? 'color-main-primary-500' : 'color-common-light-strong'})"
                  size="20px"
                />
                <span>{item.label}</span>
              </a>
              <button on:click|stopPropagation={toggleSubmenu.bind(toggleSubmenu, item)}>
                <ChevronIcon
                  color="var(--color-main-neutral-400)"
                  direction={item.expanded ? "up" : "down"}
                />
              </button>
            </li>
          {:else if item.type === "parent" && !item.url}
            <!-- Handle parent items with children that do not themselves link to any URL -->
            <li>
              <button
                typography="body-medium"
                class="item"
                title={item.label}
                on:click={toggleSubmenu.bind(toggleSubmenu, item)}
              >
                <Icon variant={item.icon} color="var(--'color-common-light-strong'})" size="20px" />
                <span>{item.label}</span>
                <ChevronIcon
                  color="var(--color-main-neutral-400)"
                  direction={item.expanded ? "up" : "down"}
                />
              </button>

              {#if item.expanded}
                <ul class="sub-menu" transition:slide={{ duration: 200 }}>
                  <!-- Handle child submenu items-->
                  {#each item.children as subItem}
                    {#if subItem.type === "link"}
                      {#if !subItem.permission || permitted($user, subItem.permission)}
                        {@const active = item.activeMatcher
                          ? item.activeMatcher($page.url.pathname)
                          : $page.url.pathname.startsWith(subItem.url)}
                        <li>
                          <a
                            href={subItem.url}
                            typography="body-medium"
                            class:active
                            class="item"
                            title={subItem.label}
                          >
                            <Icon
                              variant={subItem.icon}
                              color="var({active
                                ? '--color-main-primary-500'
                                : '--color-common-light-strong'})"
                              size="20px"
                            />
                            <span>{subItem.label}</span>
                          </a>
                        </li>
                      {/if}
                    {/if}
                  {/each}
                </ul>
              {/if}
            </li>
          {/if}
        {/if}
      {/if}
    {/each}

    <!-- Bottom Section of navbar-->

    <li>
      <button
        typography="body-medium"
        class="item logout"
        title={$t("actions.logout")}
        on:click={logout}
      >
        <Icon variant="logout" size="20px" color="var(--color-common-light-strong)" />
        <span>{$t("actions.logout")}</span>
      </button>
    </li>

    <li class="language-select">
      <LanguageSelect {compact} {transitionTimeMs} />
    </li>
  </ul>

  <Account {compact} {transitionTimeMs} />

  <button class="toggle" on:click={toggleSidebar}>
    <ChevronIcon color="var(--color-common-dark-strong)" direction={compact ? "right" : "left"} />
  </button>
</div>

<style>
  .main-menu {
    position: relative;
    display: flex;
    flex-flow: column;
    gap: 16px;
    height: 100vh;
    padding: 18px 16px;
    background-color: var(--color-common-background-light-main);
    border-right: var(--color-main-neutral-50) 1px solid;
    transition:
      width var(--transition-time) ease,
      padding var(--transition-time) ease;
  }

  .home {
    display: inline-flex;
    flex-shrink: 0;
    gap: 8px;
    align-items: center;
    padding: 8px;
    overflow: hidden;
  }

  ul {
    display: flex;
    flex-flow: column;
    gap: 2px;
    height: 100%;
    overflow: hidden auto;
    scrollbar-width: thin;
  }

  ul::-webkit-scrollbar {
    width: 10px;
  }

  .spacer {
    flex-grow: 1;
  }

  .item {
    display: flex;
    gap: 8px;
    align-items: center;
    width: 100%;
    padding: 10px 8px;
    overflow: hidden;
    color: var(--color-common-light-medium);
    text-align: left;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
  }

  .sub-menu {
    padding-left: 28px;
    transition: padding-left 200ms ease;
  }

  .compact .sub-menu {
    padding-left: 0;
  }

  .item > :global(.icon) {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
  }

  .item span {
    flex-grow: 1;
    white-space: nowrap;
    transition: opacity var(--transition-time) ease;
  }

  .main-menu.compact .item span {
    opacity: 0;
  }

  .active {
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-green);
  }

  .toggle {
    position: absolute;
    top: 54px;
    right: -12px;
    z-index: var(--z-index-overlay);
    display: flex;
    flex-shrink: 0;
    align-items: center;
    align-self: flex-end;
    justify-content: center;
    width: 24px;
    height: 24px;
    padding: 0;
    background-color: var(--color-main-primary-500);
    border: 0;
    border-radius: 50%;
    cursor: pointer;
    transition: opacity 150ms ease;
  }

  .main-menu:not(:hover) .toggle {
    opacity: 0;
  }
</style>
