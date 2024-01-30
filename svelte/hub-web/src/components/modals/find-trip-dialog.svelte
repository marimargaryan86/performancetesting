<script lang="ts">
  import { scale } from "svelte/transition";
  import { getLocaleData } from "i18n";
  import Backdrop from "components/ui/backdrop.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { validatePassengerNameRecord } from "utils/booking";
  import Icon from "components/icons/icon.svelte";
  import { goto } from "$app/navigation";
  import { URLExtended } from "utils/url";
  import routeConfig from "routeConfig";
  import { page } from "$app/stores";

  const i18n = getLocaleData();
  let backdrop: Backdrop | undefined;
  let passengerNameRecord: string;
  let passengerLastName: string;
  let passengerNameRecordError: string | boolean = false;

  export function open(): void {
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
  }

  async function search(): Promise<void> {
    passengerNameRecordError = false;
    const isPassengerNameRecordInvalid = !validatePassengerNameRecord(passengerNameRecord);

    if (isPassengerNameRecordInvalid) {
      passengerNameRecordError = $i18n.sentences.passengerNameRecordError;

      return;
    }

    await goto(
      new URLExtended(routeConfig.routes.tripManagement.routes.orders.root, {
        base: $page.url,
        query: { passengerNameRecord, passengerLastName },
      }),
    );
    close();
  }

  $: passengerNameRecord = "";
  $: passengerLastName = "";
</script>

<Backdrop bind:this={backdrop}>
  <div
    class="dialog"
    in:scale={{ duration: 150, start: 0.7, delay: 100 }}
    out:scale={{ duration: 150, start: 0.7 }}
  >
    <button class="close-icon" on:click={close}>
      <Icon variant="close" />
    </button>
    <h3 typography="headline-small" weight="bold">{$i18n.actions.findTrip}</h3>
    <div class="fields">
      <TextField
        label={$i18n.words.passengerNameRecord}
        placeholder={$i18n.sentences.passengerNameRecordPlaceholder}
        bind:value={passengerNameRecord}
        error={passengerNameRecordError}
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
      <button variant="outline" on:click={close}>{$i18n.actions.cancel}</button>
      <button variant="primary" on:click={search}>{$i18n.actions.findTrip}</button>
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

  .actions > button {
    width: 125px;
    height: 48px;
  }
</style>
