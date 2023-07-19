<script lang="ts">
  import Check from "../check.svelte";

  export let railwayOperators = [
    { label: "Renfe", isChecked: true },
    { label: "Provider2", isChecked: false },
    { label: "Provider3", isChecked: false },
    { label: "Provider4", isChecked: false },
  ];

  function clearAll(): void {
    railwayOperators.forEach(function (operator) {
      operator.isChecked = false;
    });
    railwayOperators = railwayOperators;
  }

  function selectAll(): void {
    railwayOperators.forEach(function (operator) {
      operator.isChecked = true;
    });
    railwayOperators = railwayOperators;
  }

  function handleKeyClear(event): void {
    if (event.key === "Enter") {
      clearAll();
    }
  }
  function handleKeySelect(event): void {
    if (event.key === "Enter") {
      selectAll();
    }
  }
</script>

<div class="wrapper">
  <div class="navigation typography body-small-weight-600">
    <span on:click={clearAll} on:keyup={handleKeyClear}>Clear all</span>
    <span on:click={selectAll} on:keyup={handleKeySelect}>Select all</span>
  </div>
  {#each railwayOperators as operator, index (operator)}
    <Check bind:isChecked={operator.isChecked} label={operator.label} />
  {/each}
</div>

<style>
  .wrapper {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .navigation {
    display: flex;
    gap: 16px;
  }

  .navigation span {
    color: var(--color-main-primary-500);
    cursor: pointer;
  }
</style>
