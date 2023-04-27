<script lang="ts">
  import { portal } from "directives/portal";
  import type { TransactionModel } from "models/transaction";
  import { fade, fly } from "svelte/transition";
  import Summary from "./summary.svelte";
  import Billing from "./billing.svelte";
  import Journey from "./journey/journey.svelte";
  import Passengers from "./passengers.svelte";
  import Button from "components/ui/button.svelte";

  export let value: TransactionModel | undefined;

  function close(): void {
    value = undefined;
  }
</script>

{#if value}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <div
    class="transaction-details"
    on:click|self={close}
    use:portal={document.body}
    transition:fade|local={{ duration: 200 }}
  >
    <div class="dialogue" transition:fly|local={{ duration: 200, y: 24 }}>
      <div class="header">
        <h1>
          <strong class="typography headline-small bold">ID:</strong>
          <span class="typography body-xlarge">{value.reference}</span>
        </h1>

        <h2 class="typography body-small">
          Updated: {value.createdAt.toLocaleDateString("en-GB", {
            hour: "2-digit",
            minute: "2-digit",
            year: "2-digit",
            month: "2-digit",
            day: "2-digit",
          })}
        </h2>
      </div>

      <div class="content">
        <div class="row">
          <Summary />
          <Billing />
        </div>

        <div class="row">
          <Journey />
          <Passengers />
        </div>
      </div>

      <div class="actions">
        <Button on:click={close} size="medium">Return</Button>
      </div>
    </div>
  </div>
{/if}

<style>
  .transaction-details {
    position: fixed;
    top: 0;
    left: 0;
    z-index: var(--z-index-overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background-color: rgb(0 0 0 / 0.5);
  }

  .dialogue {
    display: flex;
    flex-flow: column;
    gap: 32px;
    width: 100%;
    max-width: 960px;
    margin: 16px;
    padding: 24px 48px;
    color: var(--color-main-neutral-800);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.1);
  }

  h1 {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 4px;
    color: var(--color-main-neutral-800);
  }

  h2 {
    color: var(--color-main-neutral-700);
  }

  .content {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .content > .row {
    display: flex;
    gap: 16px;
  }

  .content > .row > :global(*) {
    flex-grow: 1;
  }

  .actions {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
  }
</style>
