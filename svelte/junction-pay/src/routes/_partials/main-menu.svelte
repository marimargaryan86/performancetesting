<script lang="ts">
  import { goto } from "$app/navigation";
  import activeLink from "$lib/actions/active-link";
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
    <a href={routeConfig.dashboard} use:activeLink={{ exact: false }}>
      <CategoryIcon /> My Dashboard
    </a>
    <a href={routeConfig.orders} class="dotted-link" use:activeLink={{ exact: false }}>My orders</a>
    <a href={routeConfig.pay} class="dotted-link" use:activeLink={{ exact: false }}>Pay</a>
    <a href={routeConfig.exchangeRates} class="dotted-link" use:activeLink={{ exact: false }}>
      FX Rates
    </a>
    <a href={routeConfig.balances.root} class="dotted-link" use:activeLink={{ exact: false }}>
      Balances
    </a>
  </nav>

  <nav class="secondary">
    <a href={routeConfig.support} class="dotted-link" use:activeLink={{ exact: false }}>Support</a>
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

  a > :global(svg),
  a::before {
    margin-right: 12px;
    width: 20px;
  }

  .main-menu > :global(svg) {
    margin: 0 auto 36px;
  }

  a {
    align-items: center;
    border-radius: 10px;
    color: var(--color-gray-light);
    display: flex;
    font-size: 16px;
    font-weight: 500;
    padding: 10px 12px;
    text-align: left;
    text-decoration: none;
    width: 100%;
  }

  a:not(:last-child) {
    margin-bottom: 14px;
  }

  nav > :global(a.active) {
    background-color: var(--color-orange-lightest);
    color: var(--color-orange);
  }

  nav > :global(a.active > svg) {
    fill: var(--color-orange);
  }

  nav > :global(.dotted-link.active::before) {
    background-color: var(--color-orange);
  }

  .dotted-link::before {
    background-color: var(--color-gray-light);
    border-radius: 50%;
    content: "";
    display: block;
    height: 20px;
  }
</style>
