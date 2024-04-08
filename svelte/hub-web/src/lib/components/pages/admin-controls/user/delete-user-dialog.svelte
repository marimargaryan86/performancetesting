<script lang="ts">
  import { getTranslator } from "$lib/i18n";
  import Dialog from "$lib/components/ui/dialogs/dialog.svelte";
  import type * as OrySchemas from "~/integration/ory/schemas";
  import { addToast } from "$lib/components/ui/toaster.svelte";
  import integrationInstancesClient from "~/integration-instances-client";
  import { createEventDispatcher } from "svelte";

  const t = getTranslator();
  const dispatch = createEventDispatcher<{ delete: void }>();

  export let maxWidth: string | undefined = undefined;
  export let user: OrySchemas.User | undefined;

  let dialog: Dialog | undefined;
  $: i18nSuccessMessage = $t("sentences.userDeleteSuccess");
  $: i18nErrorMessage = $t("sentences.userError");

  export function open(): void {
    dialog?.open();
  }

  function close(): void {
    dialog?.close();
  }

  async function deleteUser(): Promise<void> {
    try {
      if (user) {
        await integrationInstancesClient.hub.users.remove({ id: user.id });
        addToast({
          data: {
            description: i18nSuccessMessage,
            type: "success",
          },
        });
        dispatch("delete");
        close();
      }
    } catch (e) {
      addToast({
        data: {
          description: i18nErrorMessage,
          type: "error",
        },
      });
    }
  }
</script>

<Dialog bind:this={dialog} {maxWidth}>
  <div class="content">
    <h2 typography="headline-large" weight="bold">{$t("sentences.deleteUser")}</h2>
    <p typography="body-medium" class="subtitle">{user?.email}</p>
    <p typography="body-medium" class="subtitle">{$t("sentences.thisCannotBeUndone")}</p>

    <div class="actions">
      <button class="actions cancel" variant="text" size="medium" on:click={close}
        >{$t("actions.cancel")}</button
      >
      <button class="actions warn" variant="primary" size="large" on:click={deleteUser}
        >{$t("actions.deactivate")}</button
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
    align-items: center;
    justify-content: space-around;
    width: 100%;
    height: 48px;
  }

  button.actions {
    width: 100%;
    max-width: 185px;
    height: 48px;
  }

  button.actions.warn {
    background-color: var(--color-semantic-error-600);
  }

  button.actions.cancel {
    border: 1px solid var(--color-common-line-strong);
  }

  button.actions.cancel:hover {
    background-color: var(--color-common-line-soft);
  }
</style>
