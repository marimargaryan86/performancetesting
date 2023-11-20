<script lang="ts">
  import JunctionLogo from "components/icons/junction-logo.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import routeConfig from "routeConfig";
  import { pendableCall } from "utils/pendable-call";
  import { goto } from "$app/navigation";
  import Checkbox from "components/ui/checkbox.svelte";
  import passengersImage from "assets/images/passengers.png";
  import integrationInstancesClient from "integration-instances-client";

  export let data;

  let errors: string | undefined;
  let rememberMe = false;

  const { pending, func: submit } = pendableCall(async () => {
    errors = undefined;

    try {
      const user = await integrationInstancesClient.auth.signIn({
        id: data.loginFlow.id,
        data: Object.fromEntries(
          data.loginFlow.elements.map((item) => [item.attributes.name, item.attributes.value]),
        ),
        rememberMe,
      });

      const redirect =
        user.role === "reseller-admin" || user.role === "reseller-user"
          ? routeConfig.routes.tripManagement.routes.book.root
          : routeConfig.root;

      await goto(redirect, { invalidateAll: true });
    } catch {
      errors = "Invalid credentials";
    }
  });
</script>

<svelte:head>
  <title>Login · Junction Hub</title>
</svelte:head>

<main>
  <section class="intro">
    <h2 class="typography display-medium bold">Your hub for all things travel related</h2>
    <h3 class="typography body-large">Junction Hub will be the place to make and view bookings</h3>

    <img src={passengersImage} alt="" />
  </section>

  <section class="login">
    <JunctionLogo snowfallTechnology poweredBy />

    <form on:submit|preventDefault={submit}>
      {#each data.loginFlow.elements as element}
        {#if element.type === "input"}
          {#if element.attributes.type === "text" || element.attributes.type === "password"}
            <TextField
              label={element.attributes.label}
              type={element.attributes.type}
              name={element.attributes.name}
              bind:value={element.attributes.value}
              placeholder={element.attributes.label
                ? `Enter ${element.attributes.label}`
                : undefined}
              error={element.attributes.type === "password" ? errors : undefined}
            />
          {/if}
        {/if}
      {/each}

      <Button type="submit">
        Login

        {#if $pending}
          <LoadingIcon />
        {/if}
      </Button>

      <p class="typography body-small">
        We store some strictly necessary cookies. These cookies are used for Authentication and
        managing form data during a session. We currently do not use cookies for marketing,
        analytics or any other use cases.
      </p>

      <label for="remember-me" class="remember-me">
        <Checkbox id="remember-me" bind:checked={rememberMe} />
        <span class="typography body-small">Remember me for 14 days</span>
      </label>
    </form>
  </section>
</main>

<style>
  main {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    width: 100%;
    height: 100vh;
    padding: 0 16px;
  }

  main::before,
  main::after {
    position: absolute;
    top: 0;
    left: 0;
    display: block;
    height: 100%;
    content: "";
  }

  main::before {
    z-index: -2;
    width: 100%;
    background-color: var(--color-common-dark-strong);
  }

  main::after {
    z-index: -1;
    width: 50%;
    background-color: var(--color-main-primary-50);
  }

  .intro {
    display: flex;
    flex-flow: column;
    gap: 16px;
    justify-self: flex-end;
    width: 100%;
    max-width: 631px;
    padding: 54px 44px;
    color: var(--color-main-neutral-800);
  }

  .intro > img {
    width: 100%;
  }

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
</style>
