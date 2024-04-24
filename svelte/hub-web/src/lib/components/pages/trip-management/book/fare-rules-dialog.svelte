<script lang="ts">
  import { onDestroy } from "svelte";
  import Backdrop from "$lib/components/ui/backdrop.svelte";
  import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
  import { getTranslator } from "$lib/i18n";

  export let rules: MobileSchemas.TripOfferPriceQuote["rules"];

  const t = getTranslator();

  let backdrop: Backdrop | undefined = undefined;

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
    <h2 typography="display-small" weight="bold">{$t("words.fareRules")}</h2>

    {#each rules as rule}
      <h3 typography="title-small" weight="bold">{rule.title}</h3>
      <p typography="body-small">{rule.body}</p>
    {/each}

    <div class="actions">
      <button variant="primary" on:click={close}>{$t("actions.returnToBookings")}</button>
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
    width: 100%;
    max-width: 60vw;
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
