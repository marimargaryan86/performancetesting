<script lang="ts">
  import { clickOutside, movable } from "$lib/directives";
  import utils from "$lib/utils";
  import { createEventDispatcher, onMount } from "svelte";
  import { scale } from "svelte/transition";
  import CloseButton from "../buttons/close-button.svelte";

  export let title: string = undefined;
  export let focused = false;
  let windowContainer: HTMLDivElement = undefined;
  export { windowContainer as container };
  export let resizable = false;
  export let maxWidth: string = undefined;

  let alerting = false;
  let titleContainer: HTMLDivElement;

  const dispatch = createEventDispatcher<{ close: void }>();

  async function alert(): Promise<void> {
    if (!focused || alerting) {
      return;
    }

    alerting = true;
    await utils.sleep(500);
    alerting = false;
  }

  onMount(() => {
    const prevActive = document.activeElement as HTMLElement;
    windowContainer.style.left = `calc(50vw - ${windowContainer.clientWidth / 2}px)`;

    function focusIn(e: FocusEvent): void {
      if (!focused) {
        return;
      }

      if (!windowContainer.contains(document.activeElement)) {
        e.stopPropagation();
        e.preventDefault();

        windowContainer.querySelector("button").focus();

        return;
      }
    }

    window.addEventListener("focusin", focusIn);

    return () => {
      prevActive?.focus();
      window.removeEventListener("focusin", focusIn);
    };
  });
</script>

<div
  style="--max-width: {maxWidth === undefined ? 'none' : maxWidth}; --width: {maxWidth === undefined
    ? 'auto'
    : '100%'}"
  class="window"
  class:no-pointer-events={!focused}
  class:resizable
  class:alerting
  use:movable={titleContainer}
  transition:scale={{ duration: 150, start: 0.9, opacity: 0 }}
  bind:this={windowContainer}
  use:clickOutside={alert}
  on:outrostart={() => (focused = false)}
>
  <div class="title" bind:this={titleContainer}>
    <h1>{title ?? ""}</h1>

    <CloseButton on:click={() => dispatch("close")} />
  </div>

  <div class="content">
    <slot />
  </div>
</div>

<style>
  .window {
    max-width: var(--max-width);
    width: var(--width);
    background-color: var(--color-white);
    position: absolute;
    top: 30vh;
    left: 50%;
    overflow: hidden;
    border-radius: 4px;
    box-shadow: var(--drop-shadow);
    border: var(--color-gray-dark) 1px solid;
  }

  .window.resizable {
    resize: both;
  }

  .window.no-pointer-events {
    pointer-events: none;
  }

  .window.alerting {
    animation: alert 200ms linear 2;
  }

  .title {
    user-select: none;
    color: var(--color-white);
    background-color: var(--color-black);
    height: 32px;
    font-weight: 600;
    font-size: 12px;
    padding: 0 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .content {
    padding: 8px;
    background-color: var(--color-white);
  }

  @keyframes alert {
    0% {
      transform: scale(1);
      box-shadow: 0 0 16px rgba(233, 236, 47, 0.2);
    }
    50% {
      transform: scale(1.01);
      box-shadow: 0 0 16px rgba(233, 236, 47, 1);
    }
    100% {
      transform: scale(1);
      box-shadow: var(--drop-shadow);
    }
  }
</style>
