<script lang="ts">
  import Layout from "../layout.svelte";
  import Wizard from "./wizard/wizard.svelte";
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
