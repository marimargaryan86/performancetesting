<script lang="ts">
  import { goto } from "$app/navigation";
  import Button from "$lib/components/button.svelte";
  import Spinner from "$lib/components/spinner.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";
  import serviceInstances from "$services/instances";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";
  import { scale } from "svelte/transition";

  let email = "";
  let error = false;

  const { auth: service } = serviceInstances;
  const { pending, func: recoverPassword } = utils.pendableCall(
    service.recoverPassword.bind(service),
    false,
  );
  const emailStore = getContext<Writable<string>>("email");

  $: email, (error = false);

  async function reset(): Promise<void> {
    if ($pending) {
      return;
    }

    if (!email.trim().length) {
      error = true;
      return;
    }

    try {
      await recoverPassword(email);
      $emailStore = email;

      goto(routeConfig.login.passwordRecoverySent, { replaceState: true });
    } catch {
      error = true;
    }
  }
</script>

<svelte:head>
  <title>Junction | Password Reset</title>
</svelte:head>

<form class="password-recovery" on:submit|preventDefault={reset}>
  <h1>Reset Password</h1>
  <p>Enter your email address and we'll send you an email with a link to set your password</p>

  <label for="email" class:error>Email</label>
  <TextField
    type="email"
    id="email"
    bind:value={email}
    placeholder="Enter your email"
    readOnly={$pending}
    {error}
  />

  <Button type="submit">
    Reset

    {#if $pending}
      <Spinner transition={{ func: scale, params: { duration: 200 } }} />
    {/if}
  </Button>

  <a href={routeConfig.login.root}>Back to login</a>
</form>

<style>
  h1 {
    color: var(--color-gray-darkest);
    font-size: 30px;
    font-weight: 600;
    margin-bottom: 14px;
  }

  .error {
    color: var(--color-red);
  }

  p {
    color: var(--color-gray-lighter);
    font-size: 18px;
    line-height: 1.5;
    margin-bottom: 27px;
  }

  form > label {
    display: block;
    font-weight: 600;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .password-recovery > a {
    border-radius: 10px;
    color: var(--color-teal);
    display: block;
    font-weight: 600;
    margin-top: 16px;
    text-decoration: none;
    width: 100%;
  }

  .password-recovery > :global(button) {
    height: 52px;
    width: 100%;
  }

  .password-recovery > :global(.text-field) {
    display: block;
    height: 52px;
    margin-bottom: 24px;
    width: 100%;
  }

  .password-recovery > :global(button > .spinner) {
    margin-left: 8px;
    vertical-align: middle;
  }
</style>
