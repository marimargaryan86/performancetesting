<script lang="ts">
  export let compact: boolean;
  export let transitionTimeMs: number;
</script>

<img src="/images/junction/junction-icon.svg" alt="" />

<img
  src="/images/junction/junction-text.svg"
  class:compact
  class="text"
  style:--transition-time="{transitionTimeMs}ms"
  alt=""
/>

<style>
  img {
    flex-shrink: 0;
  }

  .text {
    transition: opacity var(--transition-time) ease;
  }

  .text.compact {
    opacity: 0;
  }
</style>
