<script lang="ts">
  import { goto } from "$app/navigation";
  import Button from "$lib/components/button.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import routeConfig from "$lib/route-config";
  import ListBeneficiaries from "./_components/list-beneficiaries.svelte";
  import Layout from "./_layout.svelte";
</script>

<svelte:head>
  <title>Junction | Balances</title>
</svelte:head>

<Layout>
  <div class="beneficiaries" slot="body">
    <div class="beneficiary-header">
      <div class="search">
        <TextField placeholder="Find a beneficiary" />
      </div>
      <div class="add">
        <Button on:click={() => goto(routeConfig.beneficiaries.addBeneficiary)}
          >Add beneficiary</Button
        >
      </div>
    </div>
    <div class="list">
      <ListBeneficiaries />
    </div>
  </div>
</Layout>

<style>
  .beneficiaries {
    padding: 0 49px 30px;
  }

  .add :global(button) {
    background-color: var(--color-orange);
    padding: 4px 40px;
  }

  .beneficiary-header {
    display: flex;
  }

  .search {
    flex-grow: 1;
  }

  .search :global(input) {
    width: 25%;
  }
</style>
