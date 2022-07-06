<script lang="ts">
  export let option: string;
</script>

<span>
  Junction
  {#if option === "pay"}
    <b class="pay">Pay</b>
  {:else if option === "go"}
    <b class="go">Go</b>
  {:else if option === "plus"}
    <b class="plus">Plus</b>
  {/if}
</span>

<style>
  span {
    font-weight: 700;
  }

  span > b {
    font-weight: 400;
  }

  .pay {
    color: var(--color-orange);
  }

  .go {
    color: var(--color-purple);
  }

  .plus {
    color: var(--color-blue);
  }
</style>
