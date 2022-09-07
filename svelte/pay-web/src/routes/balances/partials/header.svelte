<script lang="ts">
  import { page } from "$app/stores";
  import balanceAccounts from "$content/balance-accounts";
  import ActiveLink from "$lib/components/active-link.svelte";
  import routeConfig from "$lib/route-config";

  $: ({ subAccountId } = $page.params);
  $: subAccount = balanceAccounts.find((ba) => ba.id === subAccountId);
</script>

<div class="header">
  <div class="menu">
    <ActiveLink href={routeConfig.balances.root} exact>CC devs (220414-65188)</ActiveLink>
    <ActiveLink href={routeConfig.balances.subAccounts} exact>Sub Accounts</ActiveLink>

    {#if subAccount}
      <ActiveLink href={routeConfig.balances.subAccount(subAccountId)} exact>
        {subAccount.name}
      </ActiveLink>
    {/if}
  </div>

  <slot name="action" />
</div>

<style>
  .header {
    background-color: rgb(255 255 255 / 6%);
    border: var(--color-white) 1px solid;
    box-shadow: 0 -11px 37px rgb(0 0 0 / 3%);
    display: flex;
    height: 45px;
    justify-content: space-between;
    padding: 0 49px;
  }

  .menu {
    display: flex;
    gap: 50px;
  }

  .menu > :global(a) {
    align-items: center;
    color: var(--color-gray-lighter);
    display: flex;
    height: 100%;
    position: relative;
    text-decoration: none;
  }

  .menu > :global(a.active) {
    color: var(--color-orange);
  }

  .menu > :global(a.active::after) {
    border-bottom: var(--color-orange) 1px solid;
    bottom: -1px;
    content: "";
    display: block;
    font-weight: 600;
    height: 0;
    left: 0;
    position: absolute;
    width: 100%;
  }
</style>
