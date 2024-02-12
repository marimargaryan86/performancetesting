<script lang="ts">
  import JunctionLogo from "$lib/components/icons/junction-logo.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import Checkbox from "$lib/components/ui/checkbox.svelte";
  import { writable } from "svelte/store";
  import integrationInstancesClient from "~/integration-instances-client";
  import routeConfig from "$lib/route-config";
  import { goto, invalidateAll } from "$app/navigation";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { getPageTitle } from "$lib/utils/page-title";
  import { page } from "$app/stores";
  import { sleep } from "$lib/utils/common";
  import { getTranslator } from "$lib/i18n";

  export let data;

  let errors: string[] = [];
  let rememberMe = false;
  let form: HTMLFormElement | undefined;
  let submitButton: HTMLButtonElement | undefined;

  const t = getTranslator();
  const pending = writable<string | undefined>();

  $: form && submitButton && checkHash($page.url.hash);
  $: ({ default: defaultGroup, ...groups } = data.flow.ui.groups);

  async function checkHash(hash: string): Promise<void> {
    const match = hash.match(/^#\/\?username=(?<username>.+)&password=(?<password>.+)$/);

    if (!(match && form && submitButton instanceof HTMLButtonElement)) {
      return;
    }

    const { username, password } = match.groups ?? {};

    if (!(username && password)) {
      return;
    }

    Object.values(data.flow.ui.groups)
      .flat()
      .forEach((node) => {
        if (node.type !== "input") {
          return;
        }

        if (node.attributes.name === "password") {
          node.attributes.value = decodeURIComponent(password);
        } else if (node.attributes.name === "identifier") {
          node.attributes.value = decodeURIComponent(username);
        }
      });

    data.flow = data.flow;

    await sleep(10);

    form.requestSubmit(submitButton);
  }

  async function submit(
    event: Event & { currentTarget: EventTarget & HTMLFormElement },
  ): Promise<void> {
    if ($pending) {
      return;
    }

    const submitter =
      "submitter" in event && event.submitter instanceof HTMLButtonElement
        ? { name: event.submitter.name, value: event.submitter.value }
        : undefined;

    try {
      $pending = submitter ? `${submitter.name}:${submitter.value}` : "unknown";

      let reqData = Object.fromEntries(new FormData(event.currentTarget)) as Record<string, string>;

      if (submitter) {
        reqData[submitter.name] = submitter.value;
      }

      const result = await integrationInstancesClient.ory.auth.login({
        data: reqData,
        rememberMe,
      });

      if (result.state === "success") {
        const redirect =
          result.user.role === "reseller-admin" || result.user.role === "reseller-user"
            ? routeConfig.routes.tripManagement.routes.book.routes.train.root
            : routeConfig.root;

        return await goto(redirect, { invalidateAll: true });
      }

      data.flow = result.flow;
      errors = result.flow.ui.messages
        .filter(({ type }) => type === "error")
        .map(({ text }) => text);
    } finally {
      $pending = undefined;
    }
  }

  async function reset(): Promise<void> {
    await integrationInstancesClient.ory.auth.resetLogin();
    await invalidateAll();
  }
</script>

<svelte:head>
  <!-- TODO: Add i18n -->
  <title>{getPageTitle($t("title"), "Login")}</title>
</svelte:head>

<section class="login">
  <JunctionLogo snowfallTechnology poweredBy />

  {#if errors.length}
    <p class="errors" typography="body-small" transition:slideFade={{ duration: 300 }}>
      {errors.join(", ")}
    </p>
  {/if}

  {#each Object.values(groups) as nodes}
    <form bind:this={form} on:submit|preventDefault={submit}>
      {#each [...(defaultGroup ?? []), ...nodes] as node}
        {@const nodeError = node.messages
          .filter(({ type }) => type === "error")
          .map(({ text }) => text)}

        {#if node.type === "input"}
          {#if node.attributes.type === "hidden"}
            <input type="hidden" value={node.attributes.value} name={node.attributes.name} />
          {:else if node.attributes.type === "text" || node.attributes.type === "password"}
            <TextField
              autocomplete={node.attributes.autocomplete}
              disabled={node.attributes.disabled}
              required={node.attributes.required}
              label={node.meta.label?.text}
              type={node.attributes.name === "identifier" ? "email" : node.attributes.type}
              name={node.attributes.name}
              value={node.attributes.value}
              placeholder={node.meta.label?.text ? `Enter ${node.meta.label.text}` : undefined}
              error={nodeError.length ? nodeError : undefined}
            />
          {:else if node.attributes.type === "submit"}
            <button
              bind:this={submitButton}
              variant="primary"
              type="submit"
              value={node.attributes.value}
              name={node.attributes.name}
            >
              {node.meta.label?.text ?? "Login"}

              {#if $pending === `${node.attributes.name}:${node.attributes.value}`}
                <LoadingIcon />
              {/if}
            </button>
          {/if}
        {/if}
      {/each}
    </form>
  {/each}

  <p class="cookie-info" typography="body-small">
    <!-- TODO: Add i18n -->
    We store some strictly necessary cookies. These cookies are used for Authentication and managing
    form data during a session. We currently do not use cookies for marketing, analytics or any other
    use cases.
  </p>

  <label for="remember-me" class="remember-me">
    <Checkbox id="remember-me" bind:checked={rememberMe} />
    <!-- TODO: Add i18n -->
    <span typography="body-small">Remember me for 14 days</span>
  </label>

  <div class="actions" typography="body-medium">
    {#if data.flow.requestedAal !== "aal1"}
      <!-- TODO: Add i18n -->
      <a href={routeConfig.routes.login.root} on:click={reset}>Sign in to a different account</a>
    {:else}
      <span />
    {/if}

    <!-- TODO: Add i18n -->
    <a href={routeConfig.routes.login.routes.accountRecovery.root}>Recover account</a>
  </div>
</section>

<style>
  .login > :global(svg) {
    margin-bottom: 60px;
  }

  .login {
    display: flex;
    flex-flow: column;
    gap: 28px;
    align-items: center;
    width: 100%;
    max-width: 768px;
    padding-left: 16px;
  }

  .errors {
    color: var(--color-semantic-error-500);
  }

  form {
    display: inline-flex;
    flex-flow: column;
    gap: 24px;
    width: 100%;
    max-width: 448px;
  }

  .cookie-info {
    width: 100%;
    max-width: 448px;
  }

  .remember-me {
    display: flex;
    gap: 12px;
    align-items: center;
    width: 100%;
    max-width: 448px;
  }

  .actions {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 448px;
  }

  .actions > a {
    color: var(--color-main-primary-700);
  }
</style>
