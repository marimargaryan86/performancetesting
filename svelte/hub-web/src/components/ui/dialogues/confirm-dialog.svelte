<script lang="ts">
  import { createEventDispatcher, onDestroy } from "svelte";
  import Dialog from "./dialog.svelte";
  import { getTranslator } from "~/i18n";

  let dialog: Dialog | undefined = undefined;

  const t = getTranslator();
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
      <span>{$t("sentences.areYouSure")}</span>
    </slot>

    <div class="actions">
      <button size="small" variant="outline" on:click={cancel} style:min-width="80px">
        {$t("words.no")}
      </button>
      <button size="small" variant="primary" on:click={confirm} style:min-width="80px">
        {$t("words.yes")}
      </button>
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
