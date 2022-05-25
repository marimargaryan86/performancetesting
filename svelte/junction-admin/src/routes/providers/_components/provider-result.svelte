<script lang="ts">
  import { goto } from "$app/navigation";
  import Table from "$lib/components/ui/table.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import create from "$lib/infinite-scroll";
  import type { ProviderModel, ProviderSearchData } from "$lib/models/provider";
  import routeConfig from "$lib/route-config";
  import { conditional } from "$lib/transitions";
  import { flip } from "svelte/animate";
  import { fade, slide } from "svelte/transition";

  let _providers: ProviderModel[] = [];
  export { _providers as providers };
  export let searchData: ProviderSearchData = undefined;

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const { items: providers, depleted, pending, infiniteScroll, reset } = create(load, pageLimit);

  $: _providers = $providers;
  $: searchDataJson = JSON.stringify(searchData);
  $: searchDataJson, reset();

  async function load(pageOffset: number, pageLimit: number): Promise<ProviderModel[]> {
    try {
      return await dependencies.providerService.find(searchData, pageOffset, pageLimit);
    } catch {
      return [];
    }
  }

  function viewProvider(provider: ProviderModel): void {
    goto(routeConfig.providers.provider(provider.id));
  }
</script>

<div class="provider-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible && $providers.length}
    <Table
      on:outroend={() => (spinnerVisible = $pending)}
      stickyHeader
      transition={{ func: fade, params: { duration: transitionTimeMs } }}
    >
      <tr slot="head">
        <td>ID</td>
        <td>Name</td>
        <td>Order count</td>
      </tr>

      <svelte:fragment slot="body">
        {#each $providers as provider, idx (provider.id)}
          <tr
            title="Click to view details"
            on:click={() => viewProvider(provider)}
            style:cursor="pointer"
            in:fade={{ duration: 150, delay: (idx % pageLimit) * 15 }}
            animate:flip={{ duration: 250 }}
          >
            <td>{provider.id.substring(0, 8)}...</td>
            <td>{provider.name}</td>
            <td>{provider.orderCount}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  {:else if !spinnerVisible && $depleted && !$providers.length}
    <div
      class="empty"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <DocumentNotFoundIcon />
      <span>No providers found, try broadening your search</span>
    </div>
  {/if}

  {#if $pending && (spinnerVisible || $providers.length)}
    <div
      class="pending"
      transition:conditional|local={{
        params: { duration: transitionTimeMs },
        transition: $providers.length ? slide : fade,
      }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <SpinnerIcon />
    </div>
  {/if}
</div>

<style>
  .provider-result {
    padding: 0 8px 8px;
    overflow-y: auto;
  }

  .pending,
  .empty {
    text-align: center;
    padding: 8px;
    fill: var(--color-teal);
    user-select: none;
  }

  .empty {
    fill: var(--color-black);
    font-size: 12px;
  }

  .pending > :global(*),
  .empty > :global(*) {
    vertical-align: middle;
  }

  .provider-result > :global(.table) {
    width: 100%;
  }
</style>
