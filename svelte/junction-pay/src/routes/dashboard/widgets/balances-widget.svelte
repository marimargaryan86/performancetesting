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
      balances = await findBalances(3);
    } catch {
      //
    }
  });
</script>

<div class="balances-widget">
  {#each balances as balance}
    <article class="balance">
      <img src="/images/currency-flags/{balance.code.toLowerCase()}.png" alt="" />

      <span>{balance.code} Balance</span>

      <strong>{utils.formatCurrency(balance.amount, balance.code)}</strong>
    </article>
  {/each}
</div>

<style>
  .balances-widget {
    display: grid;
    gap: 22px;
    grid-template-columns: repeat(3, calc(33% - 11px));
  }

  .balance {
    background-color: var(--color-white);
    border-radius: 10px;
    padding: 20px;
  }

  img {
    border: var(--color-gray-lightest) 1px solid;
    border-radius: 5px;
    display: block;
    height: 38px;
    margin-bottom: 39px;
    object-fit: cover;
    width: 58px;
  }

  span {
    color: var(--color-gray-lighter);
    display: block;
    font-size: 15px;
    margin-bottom: 18px;
  }

  strong {
    font-size: 36px;
    font-weight: 600;
  }
</style>
