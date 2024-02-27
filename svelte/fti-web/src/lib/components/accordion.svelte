<script lang="ts">
  export let open = false;
  import { slide } from "svelte/transition";

  function handleClick(): boolean {
    return (open = !open);
  }
</script>

<div class="accordion">
  <button class="header" on:click={handleClick}>
    <div class="text">
      <slot name="head" />
    </div>
  </button>

  {#if open}
    <div class="details" transition:slide>
      <slot name="details" />
    </div>
  {/if}
</div>

<style>
  .accordion {
    margin: 0;
  }

  .header {
    display: flex;
    width: 100%;
    padding: 16px 24px;
    border: none;
    background-color: white;
  }

  div.details {
    padding: 0 1rem 1rem 1rem;
  }
</style>
