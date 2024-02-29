<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import Dialog from "./dialog.svelte";

  const t = getTranslator();

  export let maxWidth: string | undefined = undefined;

  let dialog: Dialog | undefined;
  let _message: string;

  export function open(message: string): void {
    _message = message;
    dialog?.open();
  }

  function close(): void {
    dialog?.close();
  }
</script>

<Dialog bind:this={dialog} {maxWidth}>
  <div class="content">
    <span typography="body-large">{_message}</span>

    <button variant="primary" size="small" on:click={close}>{$t("words.ok")}</button>
  </div>
</Dialog>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-items: center;
    text-align: center;
  }

  button {
    width: 100%;
    max-width: 80px;
  }
</style>
