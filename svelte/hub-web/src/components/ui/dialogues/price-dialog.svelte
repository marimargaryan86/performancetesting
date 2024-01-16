<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from "svelte";
  import { scale } from "svelte/transition";
  import Backdrop from "../backdrop.svelte";
  import { formatAmount } from "formatting/currency";
  import type { Price } from "integration/common/schemas/price";
  import { getLocale, getLocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";

  export let originalPrice: Price;
  export let newPrice: Price;

  let backdrop: Backdrop | undefined = undefined;

  const locale = getLocale();
  const i18n = getLocaleData();
  const dispatch = createEventDispatcher<{ cancel: void }>();

  function close(): void {
    backdrop?.close();
  }

  function cancel(): void {
    close();
    dispatch("cancel");
  }

  onMount(() => {
    if (
      !(originalPrice.currency === newPrice.currency && originalPrice.amount === newPrice.amount)
    ) {
      backdrop?.open();
    }
  });

  onDestroy(close);
</script>

<Backdrop bind:this={backdrop} closeOnClickOutside={false}>
  <div
    class="content"
    in:scale={{ duration: 150, start: 0.7, delay: 100 }}
    out:scale={{ duration: 150, start: 0.7 }}
  >
    <Icon variant="alert-disc" color="var(--color-semantic-error-500)" size="64px" />

    <h1 typography="display-small" weight="bold" class="title">{$i18n.sentences.priceChange}</h1>

    <p typography="body-medium">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html $i18n.sentences.priceChangeInfo
        .replace("{originalPrice}", formatAmount(originalPrice, { locale: $locale, sign: true }))
        .replace("{newPrice}", formatAmount(newPrice, { locale: $locale, sign: true }))}
    </p>

    <div class="actions">
      <button variant="primary" size="small" on:click={close}>
        {$i18n.actions.continue}
      </button>
      <button size="small" variant="outline" on:click={cancel} style:min-width="80px">
        {$i18n.actions.cancel}
      </button>
    </div>
  </div>
</Backdrop>

<style>
  .content {
    display: flex;
    flex-direction: column;
    gap: 24px;
    align-items: center;
    width: 100%;
    max-width: 540px;
    padding: 48px;
    text-align: center;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .actions {
    display: flex;
    flex-flow: column;
    gap: 16px;
    align-self: stretch;
    margin-top: 16px;
  }

  .actions > button {
    height: 48px;
  }
</style>
