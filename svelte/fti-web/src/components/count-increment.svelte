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
    border-radius: 40px;
    background: var(--FTI-Colours-FTI-Grey, #eee);
    padding: 5px 15px;
    height: 44px;
  }

  .inc-button {
    border: none;
    padding: 0;
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
    padding: 0 20px;
    text-align: center;
    background-color: var(--FTI-Colours-FTI-Grey, #eee);
    margin: 0;
    color: var(--Text-Dark-Text, #1c1c1c);
    text-align: center;
    font-family: "Plus Jakarta Sans";
    font-size: 18px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
  }
</style>
