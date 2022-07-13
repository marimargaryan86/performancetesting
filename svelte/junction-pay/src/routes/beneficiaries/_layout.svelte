<script lang="ts">
  import Layout from "../_layout.svelte";
  import Header from "./_partials/header.svelte";
</script>

<Layout>
  <h1 class="title" slot="head">Beneficiaries</h1>

  <div class="content" slot="body">
    <Header />

    <slot name="body" />
  </div>
</Layout>

<style>
  .title {
    font-size: 25px;
    font-weight: 700;
  }

  .content {
    display: grid;
    grid-template-rows: 50px 1fr;
  }
</style>
