<script lang="ts">
  import Switch from "../switch.svelte";
</script>

<div class="per-person-container">
  <div class="filter-heading">
    <span class="heading">Filters</span>
    <button class="clear-all">Clear All filters</button>
  </div>
  <div class="filter-content">
    <span class="filter-item">Per Person</span>
    <Switch />
    <span class="total">Total Price</span>
  </div>
</div>

<style>
  .per-person-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 28px 24px;
    background-color: white;
    border-radius: 8px;
  }

  .filter-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .heading {
    color: var(--text-dark, #1c1c1c);
    font-weight: 600;
    font-size: 20px;
    text-transform: capitalize;
  }

  .filter-content {
    display: flex;
    align-items: center;
  }

  .filter-item {
    color: var(--text-dark, #1c1c1c);
    font-weight: 600;
    font-size: 16px;
  }

  .total {
    color: var(--text-dark, #1c1c1c);
    font-weight: 400;
    font-size: 16px;
    line-height: 24px;
  }

  .clear-all {
    background: none;
    border: none;
  }
</style>
