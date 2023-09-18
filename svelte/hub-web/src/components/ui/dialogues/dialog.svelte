<script lang="ts">
  import { scale } from "svelte/transition";
  import Backdrop from "../backdrop.svelte";

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
</script>

<Backdrop on:close on:open bind:this={backdrop}>
  <div class="dialog" transition:scale={{ duration: 150, start: 0.7, delay: 100 }}>
    <slot />
  </div>
</Backdrop>

<style>
  .dialog {
    padding: 16px;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
