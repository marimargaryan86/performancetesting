<script lang="ts">
  import Table from "$lib/components/ui/table.svelte";
  import OverviewIcon from "$lib/icons/overview-icon.svelte";
  import type { ResellerModel } from "$lib/models/reseller";

  export let reseller: ResellerModel;
</script>

<div class="reseller">
  <section class="overview">
    <h2><OverviewIcon /> <span>Overview</span></h2>

    <Table>
      <tr slot="head">
        <td>ID</td>
        <td>Name</td>
        <td>Order count</td>
      </tr>

      <tr slot="body">
        <td>{reseller.id}</td>
        <td>{reseller.name}</td>
        <td>{reseller.orderCount}</td>
      </tr>
    </Table>
  </section>
</div>

<style>
  .reseller {
    padding: 8px;
  }

  section {
    box-shadow: var(--drop-shadow-light);
  }

  h2 {
    user-select: none;
    padding: 8px;
    background-color: var(--color-teal);
  }

  h2 > :global(*) {
    vertical-align: middle;
    color: var(--color-white);
    fill: var(--color-white);
    font-size: 16px;
  }

  section > :global(.table) {
    width: 100%;
  }

  section:not(:last-child) {
    margin-bottom: 16px;
  }
</style>
