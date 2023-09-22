<script lang="ts">
  import { createEventDispatcher, onDestroy } from "svelte";
  import Button from "../button.svelte";
  import Dialog from "./dialog.svelte";

  let dialog: Dialog | undefined = undefined;

  const dispatch = createEventDispatcher<{ confirm: void; cancel: void }>();

  function confirm(): void {
    dialog?.close();
    dispatch("confirm");
  }

  function cancel(): void {
    dialog?.close();
    dispatch("cancel");
  }

  export function open(): void {
    dialog?.open();
  }

  export function close(): void {
    dialog?.close();
  }

  export function toggle(): void {
    dialog?.toggle();
  }

  onDestroy(close);
</script>

<Dialog bind:this={dialog} on:close on:open>
  <div class="content">
    <slot>
      <span>Are you sure?</span>
    </slot>

    <div class="actions">
      <Button size="small" variant="outline" on:click={cancel} minWidth="80px">No</Button>
      <Button size="small" on:click={confirm} minWidth="80px">Yes</Button>
    </div>
  </div>
</Dialog>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }
</style>
