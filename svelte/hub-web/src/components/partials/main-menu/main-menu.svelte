<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import LogoutIcon from "components/icons/logout-icon.svelte";
  import Account from "./account.svelte";
  import Menu from "./menu.svelte";
  import HubLogo from "components/icons/hub-logo.svelte";
  import InformationIcon from "components/icons/information-icon.svelte";
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import { callAction } from "utils/common";

  let expanded = true;

  const transitionTimeMs = 250;

  function toggle(): void {
    expanded = !expanded;
  }

  function logout(): void {
    callAction({ action: routeConfig.routes.login.actions.logout });
  }
</script>

<nav class="main-menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  <HubLogo showText={expanded} {transitionTimeMs} />

  <button class="toggle" on:click={toggle}>
    <ChevronIcon color="var(--color-common-dark-strong)" direction={expanded ? "left" : "right"} />
  </button>

  <Menu {expanded} {transitionTimeMs} />

  <hr />

  <ul>
    <li>
      <a
        class="link typography body-medium"
        title={expanded ? undefined : "Help"}
        href={routeConfig.routes.help.routes.privacyPolicy.root}
        class:active={$page.url.pathname.includes("help")}
      >
        <InformationIcon
          color="var({$page.url.pathname.includes('help')
            ? '--color-main-primary-500'
            : '--color-common-light-strong'})"
        />
        <span>Help</span>
      </a>
    </li>
    <li>
      <button
        class="logout typography body-medium"
        title={expanded ? undefined : "Logout"}
        on:click={logout}
      >
        <LogoutIcon color="var(--color-common-light-strong)" />
        <span>Logout</span>
      </button>
    </li>
  </ul>

  <Account {expanded} {transitionTimeMs} />
</nav>

<style>
  .main-menu {
    z-index: 50;
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 240px;
    height: 100vh;
    padding: 24px 16px;
    overflow: hidden auto;
    background-color: var(--color-common-background-light-main);
    border-right: var(--color-main-neutral-50) 1px solid;
    transition: width var(--transition-time) ease, padding var(--transition-time) ease;
  }

  .main-menu:not(.expanded) {
    width: 68px;
  }

  .main-menu > :global(.hub-logo) {
    flex-shrink: 0;
    align-self: center;
    transition: margin var(--transition-time) ease;
  }

  .main-menu:not(.expanded) > :global(.hub-logo) {
    margin-left: 130px;
  }

  .toggle {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    align-self: flex-end;
    justify-content: center;
    width: 24px;
    height: 24px;
    margin: -8px -16px -8px 0;
    padding: 0;
    background-color: var(--color-main-primary-500);
    border: 0;
    border-radius: 50%;
    cursor: pointer;
    opacity: 0;
    transition: opacity 150ms ease;
  }

  .main-menu:hover > .toggle {
    opacity: 1;
  }

  .logout > span,
  .link > span {
    transition: opacity var(--transition-time) ease;
  }

  .toggle > :global(svg) {
    flex-shrink: 0;
    width: 16px;
    height: 16px;
    margin-left: -2px;
  }

  .main-menu:not(.expanded) > .toggle > :global(svg) {
    margin-left: 2px;
  }

  hr {
    flex-grow: 1;
    margin: 0 -16px;
    border: var(--color-main-neutral-50) 0 solid;
    border-bottom-width: 1px;
  }

  .logout,
  .link {
    display: flex;
    gap: 8px;
    align-items: center;
    align-self: flex-start;
    justify-content: flex-start;
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

  .logout > :global(svg),
  .link > :global(svg) {
    flex-shrink: 0;
  }

  .main-menu:not(.expanded) .logout > span,
  .main-menu:not(.expanded) .link > span {
    opacity: 0;
  }

  .active {
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-green);
  }
</style>
