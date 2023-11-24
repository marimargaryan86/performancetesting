<script lang="ts">
  import JunctionLogo from "components/icons/junction-logo.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import Checkbox from "components/ui/checkbox.svelte";
  import { writable } from "svelte/store";
  import integrationInstancesClient from "integration-instances-client";
  import routeConfig from "routeConfig";
  import { goto } from "$app/navigation";

  export let data;

  let errors: string | undefined;
  let rememberMe = false;

  const pending = writable(false);

  async function submit(
    event: Event & { currentTarget: EventTarget & HTMLFormElement },
  ): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;
      errors = undefined;

      const user = await integrationInstancesClient.ory.auth.login({
        id: data.flow.id,
        data: Object.fromEntries(new FormData(event.currentTarget)),
        rememberMe,
      });

      const redirect =
        user.role === "reseller-admin" || user.role === "reseller-user"
          ? routeConfig.routes.tripManagement.routes.book.root
          : routeConfig.root;

      await goto(redirect, { invalidateAll: true });
    } catch {
      errors = "Invalid credentials";
    } finally {
      $pending = false;
    }
  }
</script>

<svelte:head>
  <title>Login · Junction Hub</title>
</svelte:head>

<section class="login">
  <JunctionLogo snowfallTechnology poweredBy />

  <form on:submit|preventDefault={submit}>
    {#each Object.values(data.flow.ui.groups).flat() as node}
      {#if node.type === "input"}
        {#if node.attributes.type === "hidden"}
          <input type="hidden" value={node.attributes.value} name={node.attributes.name} />
        {:else if node.attributes.type === "text" || node.attributes.type === "password"}
          <TextField
            autocomplete={node.attributes.autocomplete}
            disabled={node.attributes.disabled}
            required={node.attributes.required}
            label={node.meta.label?.text}
            type={node.attributes.type}
            name={node.attributes.name}
            value={node.attributes.value ?? ""}
            placeholder={node.meta.label?.text ? `Enter ${node.meta.label.text}` : undefined}
            error={node.attributes.type === "password" ? errors : undefined}
          />
        {:else if node.attributes.type === "submit"}
          <input type="hidden" value={node.attributes.value} name={node.attributes.name} />

          <Button type="submit">
            {node.meta.label?.text ?? "Login"}

            {#if $pending}
              <LoadingIcon />
            {/if}
          </Button>
        {/if}
      {/if}
    {/each}

    <p class="typography body-small">
      We store some strictly necessary cookies. These cookies are used for Authentication and
      managing form data during a session. We currently do not use cookies for marketing, analytics
      or any other use cases.
    </p>

    <label for="remember-me" class="remember-me">
      <Checkbox id="remember-me" bind:checked={rememberMe} />
      <span class="typography body-small">Remember me for 14 days</span>
    </label>

    <a
      class="account-recovery typography body-medium"
      href={routeConfig.routes.login.routes.accountRecovery.root}
    >
      Recover account
    </a>
  </form>
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

  form {
    display: inline-flex;
    flex-flow: column;
    gap: 24px;
    width: 100%;
    max-width: 448px;
  }

  .remember-me {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .account-recovery {
    align-self: flex-end;
    color: var(--color-main-primary-700);
  }
</style>
