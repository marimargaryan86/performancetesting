<script lang="ts" context="module">
  export const HUB_URL_COOKIE_NAME = "hub-url";
</script>

<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import { page } from "$app/stores";
  import { getTranslator } from "$lib/i18n";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getUser } from "$lib/utils/permissions";
  import { onMount } from "svelte";
  import integrationInstancesClient from "~/integration-instances-client";

  export let data;

  const t = getTranslator();
  const user = getUser();

  let frame: HTMLIFrameElement | undefined;
  let url = data.url;
  let src = url;
  let loginSuccessful: boolean | undefined;

  function updateUrl(): void {
    url = frame?.contentWindow?.location.toString() ?? url;
    document.cookie = `${HUB_URL_COOKIE_NAME}=${url}; path=/; samesite=lax;`;
  }

  async function loginUser(): Promise<void> {
    const match = $page.url.hash.match(/^#\/\?username=(?<username>.+)&password=(?<password>.+)$/);

    if (!match) {
      return;
    }

    const { username, password } = match.groups ?? {};

    if (!(username && password)) {
      return;
    }

    try {
      await integrationInstancesClient.ory.auth.directLogin({
        username: decodeURI(username),
        password: decodeURI(password),
      });

      await invalidateAll();
      loginSuccessful = true;
    } catch {
      loginSuccessful = false;
    }
  }

  onMount(() => {
    src = url;
    setInterval(updateUrl, 1000);

    if (!$user) {
      loginUser();
    }
  });
</script>

<svelte:head>
  <title>{getPageTitle($t("title"))}</title>
</svelte:head>

{#if $user}
  <iframe bind:this={frame} title="Junction Hub Grupo Gea" {src} />
{:else if loginSuccessful === undefined}
  <div class="loading" typography="headline-large">Loading Junction Hub</div>
{:else if !loginSuccessful}
  <div class="login-failed" typography="headline-large">Login failed</div>
{/if}

<style>
  iframe {
    width: 100%;
    height: 100vh;
    vertical-align: top;
  }

  .loading,
  .login-failed {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
  }
</style>
