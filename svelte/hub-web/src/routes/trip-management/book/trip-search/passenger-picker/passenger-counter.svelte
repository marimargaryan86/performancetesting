<script lang="ts">
  export let label: string;
  export let amount: number;

  function increment(): void {
    amount = Math.min(20, amount + 1);
  }

  function decrement(): void {
    amount = Math.max(0, amount - 1);
  }
</script>

<div class="passenger-counter">
  <strong class="typography label-large">{label}</strong>

  <div class="counter">
    <button class="counter-btn" on:click={decrement} type="button"> - </button>

    <span class="typography body-medium">{amount}</span>

    <button on:click={increment} type="button"> + </button>
  </div>
</div>

<style>
  .passenger-counter {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .counter {
    display: flex;
    align-items: center;
    width: 100px;
  }

  span {
    flex-grow: 1;
    text-align: center;
  }

  button {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
    border: 0;
    border-radius: 8px;
    cursor: pointer;
  }

  button:hover {
    background-color: var(--color-main-primary-600);
  }
</style>
