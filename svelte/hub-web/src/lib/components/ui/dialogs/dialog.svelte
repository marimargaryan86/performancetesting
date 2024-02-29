<script lang="ts">
  import { scale } from "svelte/transition";
  import Backdrop from "../backdrop.svelte";
  import { onDestroy } from "svelte";

  export let maxWidth: string | undefined = undefined;

  let backdrop: Backdrop | undefined = undefined;

  export function open(): void {
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
  }

  export function toggle(): void {
    backdrop?.toggle();
  }

  onDestroy(close);
</script>

<Backdrop on:close on:open bind:this={backdrop}>
  <div
    class="dialog"
    style:max-width={maxWidth}
    in:scale={{ duration: 150, start: 0.7, delay: 100 }}
    out:scale={{ duration: 150, start: 0.7 }}
  >
    <slot />
  </div>
</Backdrop>

<style>
  .dialog {
    max-width: var(--max-width);
    padding: 16px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
