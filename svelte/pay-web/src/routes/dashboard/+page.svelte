<script lang="ts">
  import ordersData from "$content/orders";
  import promotedRateData from "$content/promoted-rate";
  import ratesData from "$content/rates";
  import type { Fluctuation, Order, Rate } from "$models/pay-models";
  import Layout from "../layout.svelte";
  import BalancesWidget from "./widgets/balances-widget.svelte";
  import ExchangeRatesWidget from "./widgets/exchange-rates-widget/exchange-rates-widget.svelte";
  import OrdersWidget from "./widgets/orders-widget.svelte";
  import PaymentsWidget from "./widgets/payments-widget/payments-widget.svelte";

  const orders: Order[] = ordersData as Order[];
  const promoted: Fluctuation = promotedRateData;
  const rates: Rate[] = ratesData;
</script>

<svelte:head>
  <title>Junction | Dashboard</title>
</svelte:head>

<Layout>
  <h1 class="title" slot="head">My <b>Pay Dashboard</b></h1>

  <div class="dashboard" slot="body">
    <div class="column-left">
      <BalancesWidget />

      <OrdersWidget {orders} />
    </div>

    <div class="column-right">
      <ExchangeRatesWidget {promoted} {rates} />

      <PaymentsWidget />
    </div>
  </div>
</Layout>

<style>
  .title {
    font-family: Raleway, Arial, Helvetica, sans-serif;
    font-size: 25px;
    font-weight: 300;
  }

  .title > b {
    font-weight: 500;
  }

  .dashboard {
    display: grid;
    gap: 20px;
    grid-template-columns: 1fr 467px;
  }

  .dashboard > :global(header) {
    grid-column: 1 / -1;
  }

  .column-left {
    padding: 0 0 0 49px;
  }

  .column-right {
    padding: 0 49px 0 0;
  }

  .column-left > :global(:not(:first-child)),
  .column-right > :global(:not(:first-child)) {
    margin-top: 35px;
  }
</style>
