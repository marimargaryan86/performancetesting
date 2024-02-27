<script lang="ts">
  import FaPlus from "svelte-icons/fa/FaPlus.svelte";
  import FaMinus from "svelte-icons/fa/FaMinus.svelte";
  export let value: number = 0;

  function increment(): void {
    value += 1;
  }

  function decrement(): void {
    if (value > 0) {
      value -= 1;
    }
  }
</script>

<div class="passenger-count">
  <button class="inc-button" on:click={decrement}>
    <div class="icon">
      <FaMinus />
    </div>
  </button>
  <p class="passenger-value">{value}</p>
  <button class="inc-button" on:click={increment}>
    <div class="icon">
      <FaPlus />
    </div>
  </button>
</div>

<style>
  .passenger-count {
    display: flex;
    align-items: center;
    height: 44px;
    padding: 5px 15px;
    background: var(--fti-colours-grey, #eeeeee);
    border-radius: 40px;
  }

  .inc-button {
    padding: 0;
    border: none;
  }

  .inc-button:hover {
    cursor: pointer;
  }

  .icon {
    width: 24px;
    height: 24px;
  }

  .passenger-value {
    width: 14px;
    margin: 0;
    padding: 0 20px;
    color: var(--text-dark-text, #1c1c1c);
    font-weight: 500;
    font-size: 18px;
    font-family: "Plus Jakarta Sans";
    font-style: normal;
    line-height: normal;
    text-align: center;
    background-color: var(--fti-colours-grey, #eeeeee);
  }
</style>
