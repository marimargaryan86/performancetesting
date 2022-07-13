<script lang="ts">
  import Wizard from "./_components/wizard/wizard.svelte";
  import Layout from "./_layout.svelte";
</script>

<svelte:head>
  <title>Junction | Balances</title>
</svelte:head>

<Layout>
  <div class="add-beneficiary" slot="body">
    <Wizard />
  </div>
</Layout>

<style>
  .add-beneficiary {
    padding: 0 49px 30px;
  }

  .add-beneficiary > :global(.wizard) {
    margin: 0 auto;
    max-width: 958px;
    width: 100%;
  }
</style>
