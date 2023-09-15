<script lang="ts">
  import { portal } from "directives/portal";
  import { createEventDispatcher } from "svelte";
  import { fade } from "svelte/transition";

  let show = false;

  const dispatch = createEventDispatcher<{ close: void }>();

  export function open(): void {
    show = true;
  }

  export function close(): void {
    show = false;
    dispatch("close");
  }

  export function toggle(): void {
    show = !show;
  }
</script>

{#if show}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
  <div
    class="backdrop"
    use:portal={document.body}
    role="dialog"
    on:click|self={close}
    transition:fade={{ duration: 150 }}
  >
    <slot />
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    top: 0;
    left: 0;
    z-index: var(--z-index-overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background-color: rgb(0 0 0 / 0.5);
  }
</style>
