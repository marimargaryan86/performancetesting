<script lang="ts">
  import { goto } from "$app/navigation";
  import Button from "$lib/components/button.svelte";
  import routeConfig from "$lib/route-config";
  import instances from "$services/instances";
  import { onMount } from "svelte";
  import Layout from "./_layout.svelte";

  const { balance: service } = instances;

  onMount(async () => {
    await service.findBalances();
  });
</script>

<svelte:head>
  <title>Junction | Balances</title>
</svelte:head>

<Layout>
  <div class="beneficiaries" slot="body">
    <Button on:click={() => goto(routeConfig.beneficiaries.addBeneficiary)}>Add beneficiary</Button>
  </div>
</Layout>

<style>
  .beneficiaries {
    padding: 0 49px 30px;
  }
</style>
