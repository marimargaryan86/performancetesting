<script lang="ts">
  import Table from "$lib/components/table.svelte";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";
  import type { Order } from "$models/pay-models";
  import WidgetHeader from "./widget-header.svelte";

  export let orders: Order[] = [];
</script>

<div class="orders-widget">
  <WidgetHeader viewMoreUrl={routeConfig.orders}>My orders</WidgetHeader>

  <Table>
    <thead>
      <tr>
        <th>Order reference</th>
        <th>Provider</th>
        <th>Price</th>
        <th>Status</th>
      </tr>
    </thead>

    <tbody>
      {#if !orders.length}
        <tr><td class="empty" colspan="4">No orders found</td></tr>
      {:else}
        {#each orders as order}
          <tr>
            <td class="reference">
              <strong>{order.ref}</strong>
              <span>{utils.formatDate(order.createdAt)}</span>
            </td>
            <td>{order.provider}</td>
            <td>{utils.formatCurrency(order.price.amount, order.price.code)}</td>
            <td class="status">{order.status}</td>
          </tr>
        {/each}
      {/if}
    </tbody>
  </Table>
</div>

<style>
  .orders-widget > :global(table) {
    width: 100%;
  }

  tbody::before {
    height: 12px;
  }

  td.empty {
    border-radius: 10px;
    text-align: center;
  }

  .reference > strong {
    display: block;
    margin-bottom: 6px;
  }

  .reference > span {
    color: var(--color-gray-lighter);
    font-size: 12px;
  }

  .status {
    color: var(--color-orange);
  }
</style>
