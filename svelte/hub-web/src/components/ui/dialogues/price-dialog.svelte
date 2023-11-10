<script lang="ts">
  import Button from "../button.svelte";
  import AlertIcon from "components/icons/alert-icon.svelte";
  import { createEventDispatcher, onDestroy, onMount } from "svelte";
  import { scale } from "svelte/transition";
  import Backdrop from "../backdrop.svelte";
  import { formatAmount } from "formatting/currency";
  import type { Price } from "integration/common/schemas/price";

  export let originalPrice: Price;
  export let newPrice: Price;

  let backdrop: Backdrop | undefined = undefined;

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
    <AlertIcon color="var(--color-semantic-error-500)" size="64px" variant="disc" />

    <h1 class="typography bold display-small title">Price change</h1>

    <p class="typography body-medium">
      We have noticed a price change; the initial price was
      <strong class="typography body-medium bold">{formatAmount(originalPrice, true)}</strong>, and
      the new price is
      <strong class="typography body-medium bold">{formatAmount(newPrice, true)}</strong>. Do you
      wish to continue?
    </p>

    <div class="actions">
      <Button size="small" on:click={close}>Continue</Button>
      <Button size="small" variant="outline" on:click={cancel} minWidth="80px">Cancel</Button>
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

  .actions > :global(button) {
    height: 48px;
  }
</style>
