<script lang="ts">
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { portal } from "directives/portal";
  import { createEventDispatcher } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { pendableCall } from "utils/pendable-call";
  import type { Balance } from "integration/junction-hub-api/schemas/balance";
  import type { Currency } from "integration/junction-hub-api/schemas/currency";
  import integrationInstancesClient from "integration-instances-client";

  export let accountId: string;
  export let exclude: Balance[];
  export let currencies: Map<string, Currency>;

  export function close(): void {
    visible = false;
    value = [];
    searchQuery = "";
  }

  export function open(): void {
    visible = true;
  }

  export function focusSearch(): void {
    inputRef.focus();
  }

  let value: Currency[] = [];
  let searchQuery = "";
  let visible = false;
  let inputRef: TextField<"text">;

  const dispatch = createEventDispatcher<{ addbalances: Balance[] }>();

  $: filteredBalances = Array.from(currencies.values()).filter(
    (balance) =>
      balance.code.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !exclude.find((money) => money.currencyId === balance.code),
  );

  const { pending, func: addBalances } = pendableCall(async () => {
    const balances = await Promise.all(
      value.map((item) =>
        integrationInstancesClient.hub.balances.create({
          accountId,
          data: { currencyId: item.code },
        }),
      ),
    );

    dispatch("addbalances", balances);

    close();
  });
</script>

{#if visible}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->

  <div
    class="add-balance-dialogue"
    on:click|self={close}
    use:portal={document.body}
    transition:fade={{ duration: 200 }}
  >
    <div class="dialogue" transition:fly={{ duration: 200, y: 24 }} on:introend={focusSearch}>
      <h1 class="typography headline-medium bold">Add Balances</h1>

      <TextField
        type="text"
        bind:value={searchQuery}
        placeholder="Find a balance"
        bind:this={inputRef}
      >
        <SearchIcon slot="icon-before" color="var(--color-main-neutral-400)" />
      </TextField>

      <ul class="balances typography body-large bold">
        {#each filteredBalances as balance}
          {@const id = `balance-${balance.code}`}
          <li>
            <input type="checkbox" value={balance} bind:group={value} {id} />

            <label for={id} class="balance">
              <CurrencyFlag code={balance.code} />
              <span>{balance.code}</span>
            </label>
          </li>
        {/each}
      </ul>

      <div class="actions">
        <Button on:click={close} variant="outline" size="medium">Cancel</Button>
        <Button on:click={addBalances} size="medium" disabled={!value.length}>
          Add

          {#if $pending}
            <LoadingIcon />
          {/if}
        </Button>
      </div>
    </div>
  </div>
{/if}

<style>
  .add-balance-dialogue {
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
    max-width: 480px;
    margin: 16px;
    padding: 66px 48px 48px;
    color: var(--color-main-neutral-800);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.1);
  }

  .dialogue > :global(.text-field) {
    --height: 40px;
  }

  .balances {
    display: flex;
    flex-flow: column;
    gap: 8px;
    height: 100vh;
    max-height: 312px;
    margin: 8px -24px 0;
    padding: 0 24px;
    overflow: auto;
  }

  .balance {
    display: flex;
    gap: 24px;
    align-items: center;
    padding: 16px;
    background-color: var(--color-common-background-light-main);
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
  }

  .balance > :global(.currency-flag) {
    flex-shrink: 0;
  }

  input {
    display: none;
  }

  input:checked + .balance {
    border-color: var(--color-main-primary-500);
    box-shadow: var(--shadow-small);
  }

  .actions {
    display: flex;
    gap: 16px;
  }

  .actions > :global(button) {
    flex-grow: 1;
    height: 48px;
  }
</style>
