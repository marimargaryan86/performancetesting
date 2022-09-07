<script lang="ts">
  import utils from "$lib/utils";
  import type { BalanceModel } from "$models/balance-models";
  import instances from "$services/instances";
  import { onMount } from "svelte";

  let balances: BalanceModel[] = [];

  const { balance: service } = instances;
  const { func: findBalances } = utils.pendableCall(service.findBalances.bind(service));

  onMount(async () => {
    try {
      balances = await findBalances(5);
    } catch {
      //
    }
  });
</script>

<div class="overview">
  {#each balances as balance}
    <div class="balance">
      <img src="/images/currency-flags/{balance.code.toLowerCase()}.png" alt="" />

      <p>
        <strong>{utils.formatCurrency(balance.amount)}</strong>
        <span>{balance.code}</span>
      </p>
    </div>
  {/each}
</div>

<style>
  .overview {
    display: flex;
    gap: 10px;
    padding: 0 49px;
  }

  .balance {
    background-color: var(--color-white);
    border: transparent 1px solid;
    border-radius: 10px;
    display: grid;
    gap: 10px;
    grid-template-columns: max-content 1fr;
    padding: 20px 15px;
  }

  .balance:hover {
    background-color: var(--color-orange-lightest);
    border-color: var(--color-orange);
  }

  img {
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 5px;
    width: 40px;
  }

  strong {
    display: block;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 2px;
  }

  span {
    color: var(--color-gray-lighter);
    font-size: 12px;
  }
</style>
