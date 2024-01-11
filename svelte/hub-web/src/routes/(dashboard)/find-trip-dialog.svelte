<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { scale } from "svelte/transition";
  import { getLocaleData } from "i18n";
  import Backdrop from "components/ui/backdrop.svelte";
  import CloseIcon from "components/icons/close-icon.svelte";
  import TextField from "components/ui/text-field.svelte";
  import Button from "components/ui/button.svelte";
  import { validateReferenceNumber } from "utils/booking";

  const i18n = getLocaleData();
  const dispatch = createEventDispatcher<{ search: void }>();
  let backdrop: Backdrop | undefined;
  let referenceNumber: string;
  let passengerLastName: string;
  let referenceNumberError: string | boolean = false;

  export function open(): void {
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
  }

  export function search(): void {
    referenceNumberError = false;
    const isReferenceNumberInvalid = !validateReferenceNumber(referenceNumber);

    if (isReferenceNumberInvalid) {
      referenceNumberError = $i18n.sentences.referenceNumberError;

      return;
    }

    dispatch("search");
  }

  $: referenceNumber = "";
  $: passengerLastName = "";
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
      <TextField
        label={$i18n.words.referenceNumber}
        placeholder={$i18n.sentences.referenceNumberPlaceholder}
        bind:value={referenceNumber}
        error={referenceNumberError}
      />
      <TextField
        label={`${
          $i18n.words.passenger.singular
        } ${$i18n.words.lastName.toLowerCase()} (${$i18n.words.optional.toLowerCase()})`}
        placeholder={$i18n.sentences.passengerLastNamePlaceholder}
        bind:value={passengerLastName}
      />
    </div>
    <div class="actions">
      <Button variant="outline" on:click={close}>{$i18n.actions.cancel}</Button>
      <Button on:click={search}>{$i18n.actions.findTrip}</Button>
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
