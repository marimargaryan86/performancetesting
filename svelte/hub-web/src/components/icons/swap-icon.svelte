<script lang="ts">
  export let color: string = "var(--color-main-primary-500)";
  export let size: number = 24;

  let flipped = true;

  function flipFlop(): void {
    flipped = !flipped;
  }
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  class="swap-icon"
  class:flipped
  xmlns="http://www.w3.org/2000/svg"
  on:click={flipFlop}
  on:keypress
>
  <path
    d="M8 13L4 17M4 17L8 21M4 17L20 17M16 11L20 7M20 7L16 3M20 7L4 7"
    stroke={color}
    stroke-width="1.5"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>

<style>
  .swap-icon {
    transition: transform 0.3s ease;
  }

  .swap-icon.flipped {
    transform: rotate(360deg);
  }
</style>
