<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import JunctionLogo from "components/icons/junction-logo.svelte";
  import LogoutIcon from "components/icons/logout-icon.svelte";
  import type { UserModel } from "models/user";
  import Account from "./account.svelte";
  import Menu from "./menu.svelte";

  export let user: UserModel;

  let expanded = true;

  const transitionTimeMs = 250;

  function toggle(): void {
    expanded = !expanded;
  }

  function logout(): void {
    document.cookie = "session-token=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/;";

    invalidateAll();
  }
</script>

<nav class="main-menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  <JunctionLogo size={0.5} poweredBy snowfallTechnology text={expanded} />

  <button class="toggle" on:click={toggle}>
    <ChevronIcon color="var(--color-primary-500)" direction={expanded ? "left" : "right"} />
    <span>Collapse</span>
  </button>

  <Menu {expanded} {transitionTimeMs} />

  <hr />

  <button class="logout" on:click={logout} title={expanded ? undefined : "Logout"}>
    <LogoutIcon color="var(--color-primary-500)" />
    <span>Logout</span>
  </button>

  <Account {user} {expanded} {transitionTimeMs} />
</nav>

<style>
  .main-menu {
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 236px;
    height: 100vh;
    padding: 12px;
    overflow: hidden auto;
    background-image: url("/images/main-menu-bg.png");
    background-position: bottom center;
    background-size: cover;
    transition: width var(--transition-time) ease, padding var(--transition-time) ease;
  }

  .main-menu:not(.expanded) {
    width: 54px;
    padding: 12px 8px;
  }

  .main-menu:not(.expanded) > :global(.junction-logo) {
    align-self: center;
    margin-top: 13px;
  }

  .toggle {
    display: flex;
    gap: 4px;
    align-items: center;
    align-self: flex-end;
    justify-content: flex-start;
    padding: 2px 8px 2px 4px;
    overflow: hidden;
    color: var(--color-primary-500);
    font-weight: 400;
    font-size: 10px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 24px;
    letter-spacing: 0.15px;
    background-color: transparent;
    border: 1px solid var(--color-primary-500);
    border-radius: 8px;
    cursor: pointer;
  }

  .toggle > span,
  .logout > span {
    transition: opacity var(--transition-time) ease;
  }

  .toggle > :global(svg) {
    flex-shrink: 0;
    width: 16px;
    height: 16px;
  }

  hr {
    flex-grow: 1;
    margin: 0;
    border: var(--color-neutral-700) 0 solid;
    border-bottom-width: 1px;
  }

  .logout {
    display: flex;
    gap: 8px;
    align-items: center;
    align-self: flex-start;
    justify-content: flex-start;
    width: 100%;
    padding: 10px 8px;
    overflow: hidden;
    color: var(--color-neutral-800);
    font-weight: 600;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 20px;
    letter-spacing: 0.1px;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .logout > :global(svg) {
    flex-shrink: 0;
  }

  .main-menu:not(.expanded) > .toggle {
    width: 100%;
    padding: 2px calc(50% - 8px);
  }

  .main-menu:not(.expanded) > .toggle > span,
  .main-menu:not(.expanded) > .logout > span {
    opacity: 0;
  }
</style>
