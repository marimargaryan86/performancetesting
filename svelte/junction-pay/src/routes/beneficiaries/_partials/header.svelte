<script lang="ts">
  import { page } from "$app/stores";
  import ActiveLink from "$lib/components/active-link.svelte";
  import routeConfig from "$lib/route-config";

  $: ({ pathname } = $page.url);
</script>

<div class="header">
  <ActiveLink href={routeConfig.beneficiaries.root} exact>Home</ActiveLink>

  {#if pathname === routeConfig.beneficiaries.addBeneficiary}
    <span class="chevron" />
    <ActiveLink href={routeConfig.beneficiaries.addBeneficiary} exact>Add beneficiary</ActiveLink>
  {/if}
</div>

<style>
  .header {
    height: 100%;
    padding: 0 49px;
  }

  .header > :global(a) {
    color: var(--color-gray-lighter);
    font-size: 12px;
    text-decoration: none;
  }

  .header > :global(a.active) {
    color: var(--color-orange);
  }

  .chevron {
    border: 0 solid var(--color-gray);
    border-width: 1px 1px 0 0;
    display: inline-block;
    height: 6px;
    margin: 0 8px 0 6px;
    transform: rotateZ(45deg);
    vertical-align: middle;
    width: 6px;
  }
</style>
