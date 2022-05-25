<script lang="ts" context="module">
  import type { SvelteComponent } from "svelte/internal";
  import { writable } from "svelte/store";

  type Component = { prototype: SvelteComponent };
  type DialogueProps<T extends Component> = {
    component: T;
    close: () => void;
    id: number;
    props: T["prototype"]["$set"];
  };

  let id = 0;
  // eslint-disable-next-line
  const windows = writable<DialogueProps<any>[]>([]);

  export function showDialogue<T extends Component>(
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
