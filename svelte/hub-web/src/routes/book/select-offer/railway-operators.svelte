<script lang="ts">
  import Checkbox from "../checkbox.svelte";

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

  function handleKeyClear(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      clearAll();
    }
  }
  function handleKeySelect(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      selectAll();
    }
  }
</script>

<div class="wrapper">
  <div class="navigation">
    <button class="typography body-small-weight-600" on:click={clearAll} on:keyup={handleKeyClear}>
      Clear all
    </button>
    <button
      class="typography body-small-weight-600"
      on:click={selectAll}
      on:keyup={handleKeySelect}
    >
      Select all
    </button>
  </div>

  {#each railwayOperators as operator (operator)}
    <Checkbox bind:checked={operator.isChecked} label={operator.label} />
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

  button {
    padding: 0;
    color: var(--color-main-primary-500);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
