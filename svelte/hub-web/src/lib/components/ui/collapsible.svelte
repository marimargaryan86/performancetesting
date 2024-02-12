<script lang="ts">
  import { slide } from "svelte/transition";

  let className: string | undefined = undefined;
  export { className as class };
  export let transitionTimeMs = 300;

  let expanded = false;

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    expanded ? close() : open();
  }
</script>

<div class:collapsible={true} class={className}>
  <slot name="always-visible" {open} {close} {toggle} {expanded} />

  {#if expanded}
    <div class="wrapper" transition:slide={{ duration: transitionTimeMs }}>
      <slot {open} {close} {toggle} {expanded} />
    </div>
  {/if}
</div>

<style>
  .wrapper {
    width: 100%;
  }
</style>
