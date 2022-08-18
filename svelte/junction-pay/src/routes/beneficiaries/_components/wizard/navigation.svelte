<script lang="ts">
  import Button from "$lib/components/button.svelte";

  export let goToPrevious: (() => void) | undefined = undefined;
  export let goToNext: (() => void) | undefined = undefined;
</script>

<div class="navigation">
  <slot name="previous">
    {#if goToPrevious}
      <Button on:click={goToPrevious}>Previous</Button>
    {:else}
      <span />
    {/if}
  </slot>

  <slot name="next">
    {#if goToNext}
      <Button on:click={goToNext}>Next</Button>
    {:else}
      <span />
    {/if}
  </slot>
</div>

<style>
  .navigation {
    display: flex;
    justify-content: space-between;
  }

  .navigation > :global(button) {
    background-color: var(--color-orange);
    font-size: 20px;
    height: 56px;
    width: 310px;
  }
</style>
