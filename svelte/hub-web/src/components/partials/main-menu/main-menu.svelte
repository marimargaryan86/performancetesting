<script lang="ts">
  import ChevronIcon from "~/components/icons/chevron-icon.svelte";
  import Account from "./account.svelte";
  import { page } from "$app/stores";
  import routeConfig from "~/route-config";
  import integrationInstancesClient from "~/integration-instances-client";
  import { getTranslator } from "~/i18n";
  import { goto } from "$app/navigation";
  import Icon from "~/components/icons/icon.svelte";
  import JunctionLogo from "./junction-logo.svelte";
  import { type Action, getUser, permitted } from "~/utils/permissions";
  import LanguageSelect from "./language-select.svelte";

  let compact = false;

  const user = getUser();
  const t = getTranslator();
  const transitionTimeMs = 250;

  function toggle(): void {
    compact = !compact;
  }

  async function logout(): Promise<void> {
    await integrationInstancesClient.ory.auth.logout();
    await goto(routeConfig.routes.login.root, { invalidateAll: true });
  }

  let menuItems: (
    | {
        url: string;
        label: string;
        icon: Icon["$$prop_def"]["variant"];
        activeMatcher?: (pathname: string) => boolean;
        permission?: Action;
      }
    | "spacer"
  )[];

  $: menuItems = [
    {
      url: routeConfig.routes.tripManagement.routes.book.root,
      label: $t("pages.tripManagement.pages.book.title"),
      icon: "ticket",
    },
    {
      url: routeConfig.routes.tripManagement.routes.orders.root,
      label: $t("pages.tripManagement.pages.orders.title"),
      icon: "bookings",
      permission: "journey.view",
    },
    {
      url: routeConfig.routes.pay.routes.activity.root,
      label: $t("pages.pay.pages.activity.title"),
      icon: "activity",
      permission: "transaction.view",
    },
    {
      url: routeConfig.routes.pay.routes.bills.root,
      label: $t("pages.pay.pages.bills.title"),
      icon: "bill",
      permission: "*",
    },
    "spacer",
    {
      url: routeConfig.routes.knowledgeHub.root,
      label: $t("pages.knowledgeHub.title"),
      icon: "knowledge",
    },
    {
      url: routeConfig.routes.help.routes.customerService.root,
      label: $t("actions.reportAnIssue"),
      icon: "bug",
    },
    {
      url: routeConfig.routes.help.routes.privacyPolicy.root,
      label: $t("words.help"),
      icon: "information",
      activeMatcher: (pathname): boolean =>
        pathname.startsWith(routeConfig.routes.help.root) &&
        pathname !== routeConfig.routes.help.routes.customerService.root,
    },
  ];
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
      {#if item === "spacer"}
        <li class="spacer" />
      {:else if !item.permission || permitted($user, item.permission)}
        {@const active = item.activeMatcher
          ? item.activeMatcher($page.url.pathname)
          : $page.url.pathname.startsWith(item.url)}

        <li>
          <a href={item.url} typography="body-medium" class:active class="item" title={item.label}>
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

  <button class="toggle" on:click={toggle}>
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
