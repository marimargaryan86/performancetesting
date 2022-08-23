<script lang="ts">
  import { goto } from "$app/navigation";
  import Button from "$lib/components/button.svelte";
  import Spinner from "$lib/components/spinner.svelte";
  import Switch from "$lib/components/switch.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";
  import type { AuthenticationData } from "$models/auth-models";
  import type { ValidationError } from "$models/common-models";
  import serviceInstances from "$services/instances";
  import { scale } from "svelte/transition";

  let errors: ValidationError<AuthenticationData> = {};

  const data: AuthenticationData = {
    email: "",
    password: "",
  };
  const { auth: service } = serviceInstances;
  const { pending, func: loginFunc } = utils.pendableCall(service.login.bind(service), false);

  async function login(): Promise<void> {
    if ($pending) {
      return;
    }

    errors = {};

    try {
      await loginFunc(data);

      goto(routeConfig.dashboard);
    } catch (e) {
      errors = e as typeof errors;
    }
  }
</script>

<svelte:head>
  <title>Junction | Login</title>
</svelte:head>

<form class="login" on:submit|preventDefault={login}>
  <h1>Welcome Back To Junction</h1>
  <h2>Please enter your details below</h2>

  <label for="email" class:error={!!errors.email}>Email</label>
  <TextField
    type="email"
    id="email"
    bind:value={data.email}
    placeholder="Enter your email"
    error={!!errors.email}
  />

  <label for="password" class:error={!!errors.password}>Password</label>
  <TextField
    type="password"
    id="password"
    bind:value={data.password}
    placeholder="Enter your password"
    error={!!errors.password}
  />

  <div class="actions">
    <div class="remember-me">
      <Switch id="remember-me" />
      <label for="remember-me">Remember me</label>
    </div>

    <a href={routeConfig.login.passwordRecovery}>Forgotten password</a>
  </div>

  <Button type="submit">
    Log in

    {#if $pending}
      <Spinner transition={{ func: scale, params: { duration: 200 } }} />
    {/if}
  </Button>
</form>

<style>
  h1 {
    color: var(--color-gray-darkest);
    font-size: 30px;
    font-weight: 600;
    margin-bottom: 14px;
  }

  h2 {
    color: var(--color-gray-lighter);
    font-size: 18px;
    margin-bottom: 27px;
  }

  form > label {
    display: block;
    font-weight: 600;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .error {
    color: var(--color-red);
  }

  .login > :global(button) {
    height: 52px;
    width: 100%;
  }

  .login > :global(.text-field) {
    display: block;
    height: 52px;
    margin-bottom: 36px;
    width: 100%;
  }

  .remember-me > :global(.switch) {
    margin-right: 2px;
    vertical-align: middle;
  }

  .login > :global(button > .spinner) {
    margin-left: 8px;
    vertical-align: middle;
  }

  .actions {
    align-items: center;
    display: flex;
    justify-content: space-between;
    margin-bottom: 19px;
  }

  a {
    color: var(--color-teal);
    font-weight: 600;
    text-decoration: none;
  }
</style>
