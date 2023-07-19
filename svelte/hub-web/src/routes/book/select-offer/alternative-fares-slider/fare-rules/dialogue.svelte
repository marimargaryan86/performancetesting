<script lang="ts">
  import { scale } from "svelte/transition";

  export let fareRule: string;
</script>

<div class="dialogue" transition:scale|local={{ duration: 150, start: 0.8 }}>
  <div class="typography typography body-x-small ">
    {fareRule}
  </div>
</div>

<style>
  .dialogue {
    position: absolute;
    top: 51px;
    right: -5px;
    width: 117px;
    padding: 4px 8px;
    color: var(--color-main-primary-50);
    background-color: var(--color-main-primary-600);
    border-radius: 6px;
  }
</style>
