<script lang="ts" context="module">
  function formatLanguageOption(option?: Locale): string | undefined {
    const lang = languages.find((language) => language.locale === option);

    if (!lang) {
      return "None";
    }

    return `${lang.flag}   ${lang.name}`;
  }
</script>

<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import Account from "./account.svelte";
  import Menu from "./menu.svelte";
  import SelectField from "components/ui/select-field.svelte";
  import HubLogo from "components/icons/hub-logo.svelte";
  import { page } from "$app/stores";
  import routeConfig from "routeConfig";
  import integrationInstancesClient from "integration-instances-client";
  import { getLocale, getLocaleData, type Locale } from "i18n";
  import languages from "i18n/lang/languages";
  import { goto } from "$app/navigation";
  import Icon from "components/icons/icon.svelte";

  let expanded = true;

  const locale = getLocale();
  const i18n = getLocaleData();
  const transitionTimeMs = 250;

  function toggle(): void {
    expanded = !expanded;
  }

  $: activeLink = getActiveLink($page.url.pathname);

  function getActiveLink(pathname: string): "help" | "issue" | "knowledge-hub" | undefined {
    if (pathname.startsWith(routeConfig.routes.help.routes.customerService.root)) {
      return "issue";
    }

    if (pathname.startsWith(routeConfig.routes.help.root)) {
      return "help";
    }

    if (pathname.startsWith(routeConfig.routes.knowledgeHub.root)) {
      return "knowledge-hub";
    }

    return undefined;
  }

  async function logout(): Promise<void> {
    await integrationInstancesClient.ory.auth.logout();
    await goto(routeConfig.routes.login.root, { invalidateAll: true });
  }
</script>

<nav class="main-menu" class:expanded style:--transition-time="{transitionTimeMs}ms">
  <a href={routeConfig.root} class="home">
    <HubLogo showText={expanded} {transitionTimeMs} />
  </a>

  <button class="toggle" on:click={toggle}>
    <ChevronIcon color="var(--color-common-dark-strong)" direction={expanded ? "left" : "right"} />
  </button>

  <Menu {expanded} {transitionTimeMs} />

  <hr />

  <ul>
    <li>
      <a
        typography="body-medium"
        class="link"
        title={expanded ? undefined : $i18n.pages.knowledgeHub.title}
        href={routeConfig.routes.knowledgeHub.root}
        class:active={activeLink === "knowledge-hub"}
      >
        <Icon
          variant="knowledge"
          size="20px"
          color="var({activeLink === 'knowledge-hub'
            ? '--color-main-primary-500'
            : '--color-common-light-strong'})"
        />
        <span>{$i18n.pages.knowledgeHub.title}</span>
      </a>
    </li>
    <li>
      <a
        typography="body-medium"
        class="link"
        title={expanded ? undefined : $i18n.actions.reportAnIssue}
        href={routeConfig.routes.help.routes.customerService.root}
        class:active={activeLink === "issue"}
      >
        <Icon
          variant="bug"
          color="var({activeLink === 'issue'
            ? '--color-main-primary-500'
            : '--color-common-light-strong'})"
          size="20px"
        />
        <span>{$i18n.actions.reportAnIssue}</span>
      </a>
    </li>
    <li>
      <a
        typography="body-medium"
        class="link"
        title={expanded ? undefined : $i18n.words.help}
        href={routeConfig.routes.help.routes.privacyPolicy.root}
        class:active={activeLink === "help"}
      >
        <Icon
          variant="information"
          size="20px"
          color="var({activeLink === 'help'
            ? '--color-main-primary-500'
            : '--color-common-light-strong'})"
        />
        <span>{$i18n.words.help}</span>
      </a>
    </li>
    <li>
      <button
        typography="body-medium"
        class="logout"
        title={expanded ? undefined : $i18n.actions.logout}
        on:click={logout}
      >
        <Icon variant="logout" size="20px" color="var(--color-common-light-strong)" />
        <span>{$i18n.actions.logout}</span>
      </button>
    </li>
    <li class="language-select">
      <SelectField
        options={languages.map((item) => item.locale)}
        formatter={formatLanguageOption}
        direction="up"
        bind:value={$locale}
      />
    </li>
  </ul>

  <Account {expanded} {transitionTimeMs} />
</nav>

<style>
  .main-menu {
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 240px;
    height: 100vh;
    padding: 24px 16px;
    overflow: hidden auto;
    background-color: var(--color-common-background-light-main);
    border-right: var(--color-main-neutral-50) 1px solid;
    transition:
      width var(--transition-time) ease,
      padding var(--transition-time) ease;
  }

  .home {
    transition: padding-left var(--transition-time);
  }

  .main-menu:not(.expanded) > .home {
    padding-left: 8px;
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
    white-space: nowrap;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    border-radius: 8px;
    cursor: pointer;
  }

  .logout > :global(.icon),
  .link > :global(.icon) {
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

  .main-menu :global(.select-field) {
    --height: 32px;
    --border-color: transparent;
    --border-color-focus: transparent;
    --icon-padding: 10px;
  }

  .language-select {
    margin-top: 12px;
  }
</style>
