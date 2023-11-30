<script lang="ts">
  import { onDestroy } from "svelte";
  import Button from "components/ui/button.svelte";
  import Backdrop from "components/ui/backdrop.svelte";
  import type { TripOfferPriceQuote } from "integration/junction-mobile-api/schemas/trip-offer-price-quote";

  export let priceQuote: TripOfferPriceQuote;

  let backdrop: Backdrop | undefined = undefined;

  $: rules = priceQuote.rules;

  export function open(): void {
    backdrop?.open();
  }

  export function close(): void {
    backdrop?.close();
  }

  onDestroy(close);
</script>

<Backdrop bind:this={backdrop}>
  <div class="dialog">
    <h2 class="typography display-small bold">Fare rules</h2>

    {#each rules as rule}
      <h3 class="typography title-small bold">{rule.title}</h3>
      <p class="typography body-small">{rule.body}</p>
    {/each}

    <div class="actions">
      <Button on:click={close}>Return to bookings</Button>
    </div>
  </div>
</Backdrop>

<style>
  .actions {
    position: sticky;
    bottom: -48px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin: -16px -48px -48px;
    padding: 16px 48px 48px;
    background-color: var(--color-common-background-light-main);
  }

  .dialog {
    display: flex;
    flex-flow: column;
    gap: 32px;
    max-width: minmax(400px, 50vw);
    max-height: calc(100vh - 32px);
    padding: 48px;
    overflow: auto;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .dialog h2 {
    display: flex;
    align-self: center;
  }
</style>
