<script lang="ts">
  import SelectField from "$lib/components/select-field.svelte";
  import DashboardOption from "./dashboard-option.svelte";

  export let value: string;

  const options: string[] = ["pay", "go", "plus"];
</script>

<div class="dashboard-select">
  <SelectField bind:value items={options}>
    <div class="selected" slot="head" let:value>
      <DashboardOption option={value?.toString() ?? ""} />
    </div>

    <ul class="options" let:select let:value slot="body">
      {#each options as option}
        <li class="option" aria-selected={option === value} on:click={() => select(option)}>
          <DashboardOption {option} />
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
    height: 100%;
    width: 100%;
  }

  .dashboard-select > :global(.select-field.select-field > .wrapper > .head) {
    height: 49px;
  }

  .selected {
    align-items: center;
    display: flex;
    height: 100%;
    padding: 0 12px;
  }

  .options {
    padding: 6px 0;
  }

  .option {
    cursor: pointer;
    padding: 12px;
  }

  .options:not(:hover) > .option[aria-selected="true"] {
    background-color: var(--color-light-background);
  }

  .option:hover {
    background-color: var(--color-light-background);
  }
</style>
