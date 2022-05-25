<script lang="ts">
  import { page } from "$app/stores";
  import Crossfader from "$lib/components/ui/crossfader.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { ProviderModel } from "$lib/models/provider";
  import Provider from "./_components/provider.svelte";

  const transitionTimeMs = 150;

  let pending = false;
  let provider: ProviderModel;

  $: ({ providerId } = $page.params);
  $: if (providerId) {
    pending = true;
    dependencies.providerService
      .get(providerId)
      .then((value) => (provider = value))
      .catch(() => (provider = undefined))
      .finally(() => (pending = false));
  }
</script>

<svelte:head>
  <title>Provider management | Provider details</title>
</svelte:head>

<div class="provider">
  <Crossfader active={pending ? "first" : "second"} {transitionTimeMs}>
    <div class="pending" slot="first">
      <SpinnerIcon />
    </div>

    <svelte:fragment slot="second">
      {#if provider}
        <div class="main">
          <Provider {provider} />
        </div>
      {:else}
        <div class="empty">
          <DocumentNotFoundIcon />
          <span>Provider not found</span>
        </div>
      {/if}
    </svelte:fragment>
  </Crossfader>
</div>

<style>
  .pending,
  .empty {
    text-align: center;
    padding: 8px;
    fill: var(--color-teal);
    user-select: none;
  }

  .pending > :global(*),
  .empty > :global(*) {
    vertical-align: middle;
  }

  .empty > :global(*) {
    fill: var(--color-black);
  }
</style>
