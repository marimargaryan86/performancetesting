<script lang="ts">
  import type { OrderModel, OrderSearchData } from "$lib/models/order";
  import OrderResult from "./_components/order-result.svelte";
  import OrderSearch from "./_components/order-search.svelte";

  let searchData: OrderSearchData;
  let orders: OrderModel[] = [];
</script>

<svelte:head>
  <title>Order management</title>
</svelte:head>

<div class="orders">
  <OrderSearch on:search={(e) => (searchData = e.detail)} />

  <div class="main">
    <OrderResult bind:orders {searchData} />
  </div>
</div>

<style>
  .orders {
    display: grid;
    height: 100%;
    grid-template-columns: 280px 1fr max-content;
  }

  .main {
    height: 100%;
    position: relative;
  }

  .main > :global(.order-result) {
    height: calc(100% - 8px);
    width: 100%;
    top: 8px;
    position: absolute;
  }
</style>
