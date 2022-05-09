<script lang="ts" context="module">
  import type { SvelteComponent } from "svelte/internal";
  import { writable } from "svelte/store";

  type DialogueProps<T> = { component: unknown; close: () => void; id: number; props: T };

  let id = 0;
  const windows = writable<DialogueProps<unknown>[]>([]);

  export function showDialogue<T extends { prototype: SvelteComponent }>(
    component: T,
    props: Parameters<T["prototype"]["$set"]>[0],
  ): void {
    function close(): void {
      windows.update((items) => items.filter((item) => item !== window_));
    }

    const window_: DialogueProps<T> = { props, component, close, id };
    id++;

    windows.update((items) => [...items, window_]);
  }
</script>

{#if $windows.length}
  <section class="overlay">
    {#each $windows as window_, idx (window_.id)}
      <svelte:component
        this={window_.component}
        {...window_.props}
        close={window_.close}
        focused={idx === $windows.length - 1}
      />
    {/each}
  </section>
{/if}

<style>
  .overlay {
    background-color: transparent;
    width: 100%;
    height: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 100;
  }
</style>
