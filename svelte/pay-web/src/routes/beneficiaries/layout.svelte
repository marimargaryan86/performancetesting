<script lang="ts">
  import Layout from "../layout.svelte";
  import Header from "./partials/header.svelte";
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
