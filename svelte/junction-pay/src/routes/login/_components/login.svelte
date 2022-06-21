<script lang="ts">
  import { goto } from "$app/navigation";
  import Spinner from "$lib/components/spinner.svelte";
  import Button from "$lib/components/ui/button.svelte";
  import Switch from "$lib/components/ui/switch.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import serviceInstances from "$services/instances";
  import { scale } from "svelte/transition";

  let email = "";
  let password = "";
  let error = false;
  let pending = false;

  const { auth: service } = serviceInstances;

  $: email, password, (error = false);

  async function login(): Promise<void> {
    if (pending) {
      return;
    }

    try {
      pending = true;
      await service.login(email, password);

      goto(routeConfig.dashboard);
    } catch {
      error = true;
      pending = false;
    }
  }
</script>

<form class="login" on:submit|preventDefault={login}>
  <h1>Welcome Back To Junction</h1>
  <h2>Please enter your details below</h2>

  <label for="email" class:error>Email</label>
  <TextField type="email" id="email" bind:value={email} placeholder="Enter your email" {error} />

  <label for="password" class:error>Password</label>
  <TextField
    type="password"
    id="password"
    bind:value={password}
    placeholder="Enter your password"
    {error}
  />

  <div class="actions">
    <div class="remember-me">
      <Switch id="remember-me" />
      <label for="remember-me">Remember me</label>
    </div>

    <a href="/password-recovery">Forgotten password</a>
  </div>

  <Button type="submit">
    Log in

    {#if pending}
      <Spinner transition={{ func: scale, params: { duration: 200 } }} />
    {/if}
  </Button>
</form>

<style>
  h1 {
    font-size: 30px;
    font-weight: 600;
    margin-bottom: 14px;
  }

  h2 {
    color: var(--color-gray);
    font-size: 18px;
    margin-bottom: 27px;
  }

  form > label {
    display: block;
    font-weight: 600;
    margin-bottom: 12px;
    transition: color 150ms ease;
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
