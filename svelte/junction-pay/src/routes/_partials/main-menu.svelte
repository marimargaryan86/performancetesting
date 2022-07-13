<script lang="ts">
  import { goto } from "$app/navigation";
  import ActiveLink from "$lib/components/active-link.svelte";
  import CategoryIcon from "$lib/icons/category-icon.svelte";
  import JunctionLogo from "$lib/images/junction-logo.svelte";
  import routeConfig from "$lib/route-config";
  import serviceInstances from "$services/instances";

  const { auth: service } = serviceInstances;

  async function logout(): Promise<void> {
    await service.logout();

    goto(routeConfig.login.root);
  }
</script>

<section class="main-menu">
  <JunctionLogo />

  <nav>
    <ActiveLink href={routeConfig.dashboard}>
      <CategoryIcon /> My Dashboard
    </ActiveLink>

    <ActiveLink href={routeConfig.orders} class="dotted-link">My orders</ActiveLink>
    <ActiveLink href={routeConfig.pay} class="dotted-link">Pay</ActiveLink>
    <ActiveLink href={routeConfig.exchangeRates} class="dotted-link">FX Rates</ActiveLink>
    <ActiveLink href={routeConfig.balances.root} class="dotted-link">Balances</ActiveLink>
    <ActiveLink href={routeConfig.beneficiaries.root} class="dotted-link">Beneficiaries</ActiveLink>
  </nav>

  <nav class="secondary">
    <ActiveLink href={routeConfig.support} class="dotted-link">Support</ActiveLink>
    <a href={routeConfig.login.root} class="dotted-link" on:click|preventDefault={logout}>
      Log out
    </a>
  </nav>
</section>

<style>
  .main-menu {
    background-color: var(--color-white);
    display: grid;
    grid-template-rows: max-content 1fr max-content;
    padding: 34px 12px 25px;
  }

  nav > :global(a) {
    align-items: center;
    border: transparent 1px solid;
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

  nav > :global(a > svg),
  nav > :global(a::before) {
    margin-right: 12px;
    width: 20px;
  }

  .main-menu > :global(svg) {
    margin: 0 auto 36px;
  }

  nav > :global(a:focus) {
    border-color: var(--color-teal);
    outline: 0;
  }

  nav > :global(a:not(:last-child)) {
    margin-bottom: 14px;
  }

  nav > :global(a.active) {
    background-color: var(--color-orange-lightest);
    color: var(--color-orange);
  }

  nav > :global(.dotted-link::before) {
    background-color: var(--color-gray-light);
    border-radius: 50%;
    content: "";
    display: block;
    height: 20px;
  }

  nav > :global(a.active > svg) {
    fill: var(--color-orange);
  }

  nav > :global(a.active:focus) {
    border-color: var(--color-orange);
  }

  nav > :global(.dotted-link.active::before) {
    background-color: var(--color-orange);
  }
</style>
