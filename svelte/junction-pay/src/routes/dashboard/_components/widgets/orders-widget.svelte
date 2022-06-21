<script lang="ts">
  import routeConfig from "$lib/route-config";
  import type { Order } from "$models/auth-models";
  import utils from "$lib/utils";
  import WidgetHeader from "./widget-header.svelte";

  export let orders: Order[] = [];
</script>

<div class="orders-widget">
  <WidgetHeader viewMoreUrl={routeConfig.orders}>My orders</WidgetHeader>

  <table>
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
  </table>
</div>

<style>
  table {
    border-collapse: separate;
    text-align: left;
    width: 100%;
  }

  thead > tr {
    border-radius: 10px;
    box-shadow: 0 -11px 37px rgb(0 0 0 / 3%);
    height: 45px;
  }

  th {
    background-color: rgb(255 255 255 / 20%);
    border: #ffffff 1px solid;
    border-width: 1px 0;
  }

  td,
  th {
    padding: 14px;
  }

  th:first-child {
    border-left-width: 1px;
    border-radius: 10px 0 0 10px;
  }

  th:last-child {
    border-radius: 0 10px 10px 0;
    border-right-width: 1px;
  }

  tbody::before {
    content: "";
    display: block;
    height: 12px;
  }

  td {
    background-color: var(--color-white);
    color: var(--color-gray-darker);
  }

  td:first-child,
  th:first-child {
    padding-left: 30px;
  }

  td:last-child,
  th:last-child {
    padding-right: 30px;
  }

  tr:first-child > td {
    padding-top: 30px;
  }

  tr:last-child > td {
    padding-bottom: 30px;
  }

  tr:first-child > td:not(.empty):last-child {
    border-radius: 0 10px 0 0;
  }

  tr:first-child > td:not(.empty):first-child {
    border-radius: 10px 0 0;
  }

  tr:last-child > td:not(.empty):first-child {
    border-radius: 0 0 0 10px;
  }

  tr:last-child > td:not(.empty):last-child {
    border-radius: 0 0 10px;
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
