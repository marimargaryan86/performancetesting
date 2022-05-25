<script lang="ts">
  import { page } from "$app/stores";
  import Crossfader from "$lib/components/ui/crossfader.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import type { ResellerModel } from "$lib/models/reseller";
  import Reseller from "./_components/reseller.svelte";

  const transitionTimeMs = 150;

  let pending = false;
  let reseller: ResellerModel;

  $: ({ resellerId } = $page.params);
  $: if (resellerId) {
    pending = true;
    dependencies.resellerService
      .get(resellerId)
      .then((value) => (reseller = value))
      .catch(() => (reseller = undefined))
      .finally(() => (pending = false));
  }
</script>

<svelte:head>
  <title>Reseller management | Reseller details</title>
</svelte:head>

<div class="reseller">
  <Crossfader active={pending ? "first" : "second"} {transitionTimeMs}>
    <div class="pending" slot="first">
      <SpinnerIcon />
    </div>

    <svelte:fragment slot="second">
      {#if reseller}
        <div class="main">
          <Reseller {reseller} />
        </div>
      {:else}
        <div class="empty">
          <DocumentNotFoundIcon />
          <span>Reseller not found</span>
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
