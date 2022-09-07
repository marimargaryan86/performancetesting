<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import CheckedIcon from "$lib/icons/checked-icon.svelte";
  import routeConfig from "$lib/route-config";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";

  const email = getContext<Writable<string>>("email");
</script>

<svelte:head>
  <title>Junction | Password Reset</title>
</svelte:head>

<div class="password-recovery-sent">
  <h1><CheckedIcon /><span>Password Reset</span></h1>
  <p>You should recieve a link in a few moments. Please open the link to reset your password</p>

  {#if $email.length}<strong>{$email}</strong>{/if}

  <a href={routeConfig.login.root}>
    <Button>Back to login</Button>
  </a>
</div>

<style>
  h1 {
    align-items: center;
    color: var(--color-gray-darkest);
    display: flex;
    font-size: 30px;
    font-weight: 600;
    gap: 16px;
    margin-bottom: 14px;
  }

  p {
    color: var(--color-gray-lighter);
    font-size: 18px;
    line-height: 1.5;
    margin-bottom: 27px;
  }

  strong {
    display: block;
    font-weight: 600;
    margin-bottom: 27px;
  }

  .password-recovery-sent > a {
    border-radius: 10px;
    display: block;
    width: 100%;
  }

  .password-recovery-sent > a > :global(button) {
    height: 52px;
    width: 100%;
  }
</style>
