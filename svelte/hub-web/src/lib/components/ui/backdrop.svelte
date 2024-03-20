<script lang="ts">
  import { portal } from "$lib/directives/portal";
  import { createEventDispatcher, onDestroy } from "svelte";
  import { fade } from "svelte/transition";

  export let closeOnClickOutside = true;

  let show = false;

  const dispatch = createEventDispatcher<{ close: void; open: void }>();

  export function open(): void {
    show = true;
    dispatch("open");
  }

  export function close(): void {
    show = false;
    dispatch("close");
  }

  export function toggle(): void {
    if (show) {
      close();
    } else {
      open();
    }
  }

  onDestroy(close);
</script>

{#if show}
  <div
    class="backdrop"
    use:portal={document.body}
    role="presentation"
    on:click|self={closeOnClickOutside ? close : undefined}
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
