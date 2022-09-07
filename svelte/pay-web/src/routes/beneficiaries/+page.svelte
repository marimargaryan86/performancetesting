<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import SearchIcon from "$lib/icons/search-icon.svelte";
  import routeConfig from "$lib/route-config";
  import BeneficiaryList from "./components/beneficiary-list.svelte";
  import Layout from "./layout.svelte";
</script>

<svelte:head>
  <title>Junction | Beneficiaries</title>
</svelte:head>

<Layout>
  <div class="beneficiaries" slot="body">
    <div class="header">
      <div class="search">
        <SearchIcon />
        <TextField placeholder="Search beneficiaries" />
      </div>

      <a href={routeConfig.beneficiaries.addBeneficiary}>
        <Button>+ Add beneficiary</Button>
      </a>
    </div>

    <BeneficiaryList />
  </div>
</Layout>

<style>
  .beneficiaries {
    padding: 0 49px 30px;
  }

  .header {
    display: flex;
    gap: 8px;
    justify-content: space-between;
  }

  a > :global(button) {
    background-color: var(--color-orange);
    white-space: nowrap;
  }

  .search {
    background-color: var(--color-white);
    max-width: 388px;
    width: 100%;
  }

  .search > :global(svg) {
    margin: 0 4px 0 14px;
    vertical-align: middle;
  }

  .search > :global(input) {
    background-color: transparent;
    border-color: transparent;
    padding-left: 0;
    vertical-align: middle;
  }

  .search > :global(input:focus) {
    border-color: transparent;
  }
</style>
