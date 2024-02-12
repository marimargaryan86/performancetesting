<script lang="ts">
  export let color: string = "var(--color-main-primary-500)";
  export let size: number = 24;

  const mask = 'url("/images/icons/swap-directions.svg")';

  let flipped = true;

  function flipFlop(): void {
    flipped = !flipped;
  }
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  style:mask-image={mask}
  style:-webkit-mask-image={mask}
  style:--size={size}
  style:background-color={color}
  style:width="{size}px"
  style:height="{size}px"
  class="swap-icon"
  class:flipped
  on:click={flipFlop}
  on:keypress
/>

<style>
  .swap-icon {
    transition: transform 0.3s ease;
  }

  .swap-icon.flipped {
    transform: rotate(360deg);
  }
</style>
