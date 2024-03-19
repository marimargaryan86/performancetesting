<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import Dialog from "$lib/components/ui/dialogs/dialog.svelte";

  const t = getTranslator();

  export let maxWidth: string | undefined = undefined;
  let dialog: Dialog | undefined;

  export function open(): void {
    dialog?.open();
  }

  function close(): void {
    dialog?.close();
  }
</script>

<Dialog bind:this={dialog} {maxWidth}>
  <div class="content">
    <h2 typography="headline-large" weight="bold">{$t("sentences.discardChangesTitle")}</h2>
    <p typography="body-medium" class="subtitle">
      {$t("sentences.discardChangesBody")}
    </p>

    <div class="actions">
      <button class="actions cancel" variant="text" size="medium" on:click={close}
        >{$t("actions.cancel")}</button
      >
      <a
        class="actions"
        variant="primary"
        size="large"
        on:click={close}
        href={routeConfig.routes.adminControls.routes.users.root}>{$t("actions.discard")}</a
      >
    </div>
  </div>
</Dialog>

<style>
  .content {
    display: flex;
    flex-flow: column;
    gap: 36px;
    align-items: center;
    padding: 24px;
    text-align: center;
  }

  p.subtitle {
    color: var(--color-common-light-soft);
  }

  .actions {
    display: flex;
    flex-direction: row;
    gap: 8px;
    align-items: center;
    justify-content: space-around;
    width: 100%;
    height: 48px;
  }

  button.actions,
  a.actions {
    width: 100%;
    max-width: 185px;
    height: 48px;
  }

  button.actions.cancel {
    border: 1px solid var(--color-common-line-strong);
  }

  button.actions.cancel:hover {
    background-color: var(--color-common-line-soft);
  }
</style>
