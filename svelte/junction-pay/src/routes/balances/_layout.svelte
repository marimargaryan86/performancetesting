<script lang="ts">
  import Layout from "../_layout.svelte";
  import Header from "./_partials/header.svelte";
  import Overview from "./_partials/overview.svelte";
</script>

<Layout>
  <h1 class="title" slot="head">Balances</h1>

  <div class="content" slot="body">
    <Overview />

    <Header>
      <slot name="action" slot="action" />
    </Header>

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
    gap: 39px;
    grid-template-rows: 76px max-content 1fr;
  }
</style>
