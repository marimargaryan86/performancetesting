<script lang="ts">
  import { goto } from "$app/navigation";
  import Table from "$lib/components/ui/table.svelte";
  import dependencies from "$lib/dependencies";
  import DocumentNotFoundIcon from "$lib/icons/document-not-found-icon.svelte";
  import SpinnerIcon from "$lib/icons/spinner-icon.svelte";
  import create from "$lib/infinite-scroll";
  import type { OrderModel, OrderSearchData } from "$lib/models/order";
  import routeConfig from "$lib/route-config";
  import { conditional } from "$lib/transitions";
  import utils from "$lib/utils";
  import { flip } from "svelte/animate";
  import { fade, slide } from "svelte/transition";

  let _orders: OrderModel[] = [];
  export { _orders as orders };
  export let searchData: OrderSearchData = undefined;

  let spinnerVisible = true;

  const pageLimit = 15;
  const transitionTimeMs = 150;
  const { items: orders, depleted, pending, infiniteScroll, reset } = create(load, pageLimit);

  $: _orders = $orders;
  $: searchDataJson = JSON.stringify(searchData);
  $: {
    // Reset orders when search data changes.
    searchDataJson;
    reset();
  }

  async function load(pageOffset: number, pageLimit: number): Promise<OrderModel[]> {
    try {
      return await dependencies.orderService.find(searchData, pageOffset, pageLimit);
    } catch {
      return [];
    }
  }

  function viewOrder(order: OrderModel): void {
    goto(routeConfig.orders.order(order.id));
  }
</script>

<div class="order-result" use:infiniteScroll={{ threshold: 300 }}>
  {#if !spinnerVisible && $orders.length}
    <Table
      on:outroend={() => (spinnerVisible = $pending)}
      stickyHeader
      transition={{ func: fade, params: { duration: transitionTimeMs } }}
    >
      <tr slot="head">
        <td>ID</td>
        <td>SPNR</td>
        <td>Reseller</td>
        <td>Items</td>
        <td>Price</td>
        <td>Created</td>
        <td>Last modfied</td>
        <td>Status</td>
      </tr>

      <svelte:fragment slot="body">
        {#each $orders as order, idx (order.id)}
          <tr
            title="Click to view details"
            on:click={() => viewOrder(order)}
            style:cursor="pointer"
            in:fade={{ duration: 150, delay: (idx % pageLimit) * 15 }}
            animate:flip={{ duration: 250 }}
          >
            <td>{order.id.substring(0, 8)}...</td>
            <td>{order.spnr}</td>
            <td>{order.reseller.name}</td>
            <td>{order.itemIds.length}</td>
            <td>{utils.formatPrice(order.price)}</td>
            <td>{order.createdAt.toLocaleDateString(...utils.fullDateTime)}</td>
            <td>{order.modifiedAt.toLocaleDateString(...utils.fullDateTime)}</td>
            <td>{order.status}</td>
          </tr>
        {/each}
      </svelte:fragment>
    </Table>
  {:else if !spinnerVisible && $depleted && !$orders.length}
    <div
      class="empty"
      transition:fade|local={{ duration: transitionTimeMs }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <DocumentNotFoundIcon />
      <span>No orders found, try broadening your search</span>
    </div>
  {/if}

  {#if $pending && (spinnerVisible || $orders.length)}
    <div
      class="pending"
      transition:conditional|local={{
        params: { duration: transitionTimeMs },
        transition: $orders.length ? slide : fade,
      }}
      on:outroend={() => (spinnerVisible = $pending)}
    >
      <SpinnerIcon />
    </div>
  {/if}
</div>

<style>
  .order-result {
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

  .order-result > :global(.table) {
    width: 100%;
  }
</style>
