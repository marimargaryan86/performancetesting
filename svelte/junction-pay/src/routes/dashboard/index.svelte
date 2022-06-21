<script lang="ts">
  import type { Fluctuation, Order, Rate } from "$models/pay-models";
  import Header from "./_components/header/header.svelte";
  import MainMenu from "./_components/main-menu.svelte";
  import BalancesWidget from "./_components/widgets/balances-widget.svelte";
  import ExchangeRatesWidget from "./_components/widgets/exchange-rates-widget/exchange-rates-widget.svelte";
  import OrdersWidget from "./_components/widgets/orders-widget.svelte";
  import PaymentsWidget from "./_components/widgets/payments-widget/payments-widget.svelte";

  const orders: Order[] = [...Array(6)].map(() => ({
    ref: "EH96JKL",
    createdAt: new Date("2022-07-17"),
    provider: "Detail here",
    price: { amount: 160, code: "GBP" },
    status: "Pending",
  }));
  const promoted: Fluctuation = { amount: 0.5, code: "EUR" };
  const rates: Rate[] = [
    { code: "GBP", live: -0.1234, yesterday: -0.1234, lastWeek: 1.1234 },
    { code: "EUR", live: -0.1234, yesterday: -0.1234, lastWeek: 1.1234 },
    { code: "SEK", live: -0.1234, yesterday: -0.1234, lastWeek: 1.1234 },
  ];
</script>

<svelte:head>
  <title>Junction | Dashboard</title>
</svelte:head>

<main>
  <MainMenu />

  <section class="content">
    <Header />

    <div class="column-left">
      <BalancesWidget />

      <OrdersWidget {orders} />
    </div>

    <div class="column-right">
      <ExchangeRatesWidget {promoted} {rates} />

      <PaymentsWidget />
    </div>
  </section>
</main>

<style>
  main {
    display: grid;
    grid-template-columns: 218px 1fr;
    height: 100vh;
  }

  .content {
    background-color: var(--color-light-background);
    display: grid;
    gap: 0 20px;
    grid-template-columns: 1fr 467px;
    grid-template-rows: 113px 1fr;
  }

  .content > :global(header) {
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
