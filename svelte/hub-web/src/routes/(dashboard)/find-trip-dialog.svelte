<script lang="ts">
  import { scale } from "svelte/transition";
  import { getLocaleData } from "i18n";
  import Backdrop from "components/ui/backdrop.svelte";
  import CloseIcon from "components/icons/close-icon.svelte";
  import TextField from "components/ui/text-field.svelte";
  import Button from "components/ui/button.svelte";

  const i18n = getLocaleData();
  let backdrop: Backdrop | undefined;

  export function open(): void {
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
  }
</script>

<Backdrop bind:this={backdrop}>
  <div
    class="dialog"
    in:scale={{ duration: 150, start: 0.7, delay: 100 }}
    out:scale={{ duration: 150, start: 0.7 }}
  >
    <button class="close-icon" on:click={close}>
      <CloseIcon variant="cross" />
    </button>
    <h3 class="typography headline-small bold">{$i18n.actions.findTrip}</h3>
    <div class="fields">
      <TextField label={"Reference number"} placeholder={"For example: 9A2FDF56"} />
      <TextField
        label={"Passenger surname (optional)"}
        placeholder={"As on your booking confirmation"}
      />
    </div>
    <div class="actions">
      <Button variant="outline" on:click={close}>{$i18n.actions.cancel}</Button>
      <Button>{$i18n.actions.findTrip}</Button>
    </div>
  </div>
</Backdrop>

<style>
  .dialog {
    position: relative;
    display: flex;
    flex-flow: column;
    gap: 32px;
    justify-content: space-between;
    width: 100%;
    max-width: 540px;
    height: 416px;
    padding: 32px;
    padding-top: 40px;
    overflow: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  button.close-icon {
    position: absolute;
    top: 24px;
    right: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    margin: 0;
    padding: 0;
    background-color: transparent;
    border: 0;
    border-radius: 4px;
  }

  button.close-icon:hover {
    background-color: var(--color-main-neutral-50);
    cursor: pointer;
  }

  .fields {
    display: flex;
    flex-flow: column;
    gap: 24px;
    align-items: normal;
    justify-content: center;
  }

  .actions {
    display: flex;
    flex-flow: row;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
  }

  .actions > :global(button) {
    width: 125px;
    height: 48px;
  }
</style>
