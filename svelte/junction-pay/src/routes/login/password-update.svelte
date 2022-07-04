<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import Button from "$lib/components/button.svelte";
  import Spinner from "$lib/components/spinner.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import serviceInstances from "$services/instances";
  import { scale } from "svelte/transition";

  let password = "";
  let passwordRepeat = "";
  let error = false;
  let pending = false;

  const { auth: service } = serviceInstances;

  $: code = $page.url.searchParams.get("code") ?? "";
  $: password, passwordRepeat, (error = false);

  async function updatePassword(): Promise<void> {
    if (pending) {
      return;
    }

    try {
      if (password !== passwordRepeat) {
        throw new Error("Password mismatch");
      }

      pending = true;
      await service.updatePassword(code, password);

      goto(routeConfig.login.root);
    } catch {
      error = true;
      pending = false;
    }
  }
</script>

<svelte:head>
  <title>Junction | Update Password</title>
</svelte:head>

<form class="password-update" on:submit|preventDefault={updatePassword}>
  <h1>Update Password</h1>
  <h2>Please enter your new password</h2>

  <label for="password" class:error>New password</label>
  <TextField
    type="password"
    id="password"
    bind:value={password}
    placeholder="Enter password"
    {error}
  />

  <label for="password-confirm" class:error>Confirm new password</label>
  <TextField
    type="password"
    id="password-confirm"
    bind:value={passwordRepeat}
    placeholder="Repeat password"
    {error}
  />

  <Button type="submit">
    Update password

    {#if pending}
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
  }

  .error {
    color: var(--color-red);
  }

  .password-update > :global(button) {
    height: 52px;
    width: 100%;
  }

  .password-update > :global(.text-field) {
    display: block;
    height: 52px;
    margin-bottom: 36px;
    width: 100%;
  }

  .password-update > :global(button > .spinner) {
    margin-left: 8px;
    vertical-align: middle;
  }
</style>
