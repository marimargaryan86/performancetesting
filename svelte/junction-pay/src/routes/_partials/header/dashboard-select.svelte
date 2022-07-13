<script lang="ts">
  import SelectField from "$lib/components/select-field.svelte";
  import DashboardOption, { options, type Option } from "./dashboard-option.svelte";

  export let value: Option;
</script>

<div class="dashboard-select">
  <SelectField bind:value items={options}>
    <div class="selected" slot="head" let:value>
      <DashboardOption option={value ?? "pay"} />
    </div>

    <ul class="options" let:select let:value let:items slot="body">
      {#each items as item}
        <li class="option" aria-selected={item === value} on:click={() => select(item)}>
          <DashboardOption option={item} />
        </li>
      {/each}
    </ul>
  </SelectField>
</div>

<style>
  .dashboard-select {
    height: 49px;
    min-width: 196px;
  }

  .dashboard-select > :global(.select-field.select-field) {
    font-size: 14px;
    height: 100%;
    width: 100%;
  }

  .selected {
    align-items: center;
    display: flex;
    height: 100%;
    padding: 0 12px;
  }

  .option {
    cursor: pointer;
    padding: 12px;
  }

  .option[aria-selected="true"] {
    background-color: var(--color-gray-lightest);
  }

  .option:hover {
    background-color: var(--color-light-background);
  }
</style>
