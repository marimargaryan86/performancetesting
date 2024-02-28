<script lang="ts">
  import { MAX_TOTAL_COUNT } from "$lib/models/passenger";

  export let label: string;
  export let count: number;
  export let totalCount: number;

  function increment(): void {
    count = Math.min(MAX_TOTAL_COUNT, count + 1);
  }

  function decrement(): void {
    count = Math.max(0, count - 1);
  }
</script>

<div class="passenger-counter">
  <strong typography="label-large">{label}</strong>

  <div class="counter">
    <button class="counter-btn" on:click={decrement} type="button" disabled={count === 0}>
      -
    </button>

    <span typography="body-medium">{count}</span>

    <button on:click={increment} type="button" disabled={totalCount === MAX_TOTAL_COUNT}>
      +
    </button>
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
    transition: background-color 300ms ease;
  }

  button:hover {
    background-color: var(--color-main-primary-600);
  }

  button:disabled {
    background-color: var(--color-main-neutral-200);
  }
</style>
