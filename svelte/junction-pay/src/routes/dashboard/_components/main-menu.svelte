<script lang="ts">
  import { goto } from "$app/navigation";
  import CategoryIcon from "$lib/icons/category-icon.svelte";
  import JunctionLogo from "$lib/images/junction-logo.svelte";
  import routeConfig from "$lib/route-config";
  import serviceInstances from "$services/instances";

  const { auth: service } = serviceInstances;

  async function logout(): Promise<void> {
    await service.logout();

    goto(routeConfig.login);
  }
</script>

<section class="main-menu">
  <JunctionLogo />

  <nav>
    <a href={routeConfig.dashboard} class="filled-link"><CategoryIcon /> My Dashboard</a>
    <a href={routeConfig.orders} class="dotted-link">My orders</a>
    <a href={routeConfig.pay} class="dotted-link">Pay</a>
    <a href={routeConfig.exchangeRates} class="dotted-link">FX Rates</a>
    <a href={routeConfig.balances} class="dotted-link">Balances</a>
  </nav>

  <nav class="secondary">
    <a href={routeConfig.support} class="dotted-link">Support</a>
    <a href={routeConfig.login} class="dotted-link" on:click|preventDefault={logout}>Log out</a>
  </nav>
</section>

<style>
  .main-menu {
    background-color: var(--color-white);
    display: grid;
    grid-template-rows: max-content 1fr max-content;
    padding: 34px 12px 25px;
  }

  .main-menu > :global(svg) {
    margin: 0 auto 36px;
  }

  nav > a {
    align-items: center;
    display: flex;
    font-size: 16px;
    font-weight: 500;
    padding: 10px 12px;
    text-align: left;
    text-decoration: none;
    width: 100%;
  }

  nav > a:not(:last-child) {
    margin-bottom: 14px;
  }

  .filled-link {
    background-color: var(--color-orange-lightest);
    border-radius: 10px;
    color: var(--color-orange);
    font-weight: 700;
  }

  .dotted-link {
    color: var(--color-gray-light);
  }

  .dotted-link::before {
    background-color: var(--color-gray-light);
    border-radius: 50%;
    content: "";
    display: block;
    height: 20px;
  }

  .filled-link > :global(svg),
  .dotted-link::before {
    margin-right: 12px;
    width: 20px;
  }
</style>
