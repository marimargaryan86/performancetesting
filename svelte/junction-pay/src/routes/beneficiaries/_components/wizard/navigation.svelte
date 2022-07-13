<script lang="ts">
  import Button from "$lib/components/button.svelte";

  export let goToPrevious: (() => void) | undefined = undefined;
  export let goToNext: (() => void) | undefined = undefined;
</script>

<div class="navigation">
  {#if goToPrevious}
    <Button on:click={goToPrevious}>Previous</Button>
  {:else}
    <span />
  {/if}

  {#if goToNext}
    <Button on:click={goToNext}>Next</Button>
  {:else}
    <span />
  {/if}
</div>

<style>
  .navigation {
    display: flex;
    justify-content: space-between;
    margin-top: 60px;
  }

  .navigation > :global(button) {
    background-color: var(--color-orange);
    font-size: 20px;
    height: 56px;
    width: 310px;
  }
</style>
