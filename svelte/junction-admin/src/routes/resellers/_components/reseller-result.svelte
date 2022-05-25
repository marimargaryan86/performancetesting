<script lang="ts">
  import { goto } from "$app/navigation";
  import Table from "$lib/components/ui/table.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import create from "$lib/infinite-scroll";
  import type { ResellerModel, ResellerSearchData } from "$lib/models/reseller";
  import routeConfig from "$lib/route-config";
  import { conditional } from "$lib/transitions";
  import { flip } from "svelte/animate";
  import { fade, slide } from "svelte/transition";

  let _resellers: ResellerModel[] = [];
  export { _resellers as resellers };
  export let searchData: ResellerSearchData = undefined;

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const { items: resellers, depleted, pending, infiniteScroll, reset } = create(load, pageLimit);

  $: _resellers = $resellers;
  $: searchDataJson = JSON.stringify(searchData);
  $: searchDataJson, reset();

  async function load(pageOffset: number, pageLimit: number): Promise<ResellerModel[]> {
    try {
      return await dependencies.resellerService.find(searchData, pageOffset, pageLimit);
    } catch {
      return [];
    }
  }

  function viewReseller(reseller: ResellerModel): void {
    goto(routeConfig.resellers.reseller(reseller.id));
  }
</script>

<div class="reseller-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible && $resellers.length}
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
        {#each $resellers as reseller, idx (reseller.id)}
          <tr
            title="Click to view details"
            on:click={() => viewReseller(reseller)}
            style:cursor="pointer"
            in:fade={{ duration: 150, delay: (idx % pageLimit) * 15 }}
            animate:flip={{ duration: 250 }}
          >
            <td>{reseller.id.substring(0, 8)}...</td>
            <td>{reseller.name}</td>
            <td>{reseller.orderCount}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  {:else if !spinnerVisible && $depleted && !$resellers.length}
    <div
      class="empty"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <DocumentNotFoundIcon />
      <span>No resellers found, try broadening your search</span>
    </div>
  {/if}

  {#if $pending && (spinnerVisible || $resellers.length)}
    <div
      class="pending"
      transition:conditional|local={{
        params: { duration: transitionTimeMs },
        transition: $resellers.length ? slide : fade,
      }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <SpinnerIcon />
    </div>
  {/if}
</div>

<style>
  .reseller-result {
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

  .reseller-result > :global(.table) {
    width: 100%;
  }
</style>
