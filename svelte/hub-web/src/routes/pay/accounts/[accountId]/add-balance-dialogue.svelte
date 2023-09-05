<script lang="ts">
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { portal } from "directives/portal";
  import type { Infer } from "integration/junction-mobile-api/schema-model.server";
  import type { priceModel } from "integration/junction-mobile-api/schemas/price";
  import type { CurrencyModel } from "models/money";
  import routeConfig from "routeConfig";
  import { createEventDispatcher } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { callAction } from "utils/common";

  export let accountId: string;
  export let exclude: Infer<typeof priceModel>[];
  export let currencies: Map<string, CurrencyModel>;

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

  let value: CurrencyModel[] = [];
  let searchQuery = "";
  let visible = false;
  let inputRef: TextField<"text">;
  let pending = false;

  const dispatch = createEventDispatcher<{ addbalances: Infer<typeof priceModel>[] }>();

  $: filteredBalances = Array.from(currencies.values()).filter(
    (balance) =>
      balance.code.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !exclude.find((money) => money.currency === balance.code),
  );

  async function addBalances(): Promise<void> {
    if (pending) {
      return;
    }

    pending = true;

    const result = await callAction<{ balances: Infer<typeof priceModel>[] }>({
      action: routeConfig.pay.accounts.actions.addBalances(accountId),
      data: { currencyCodes: value.map((item) => item.code) },
      dataType: "json",
      apply: false,
    });

    if (result.type === "success") {
      dispatch("addbalances", result.data?.balances ?? []);
    }

    pending = false;
    close();
  }
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

          {#if pending}
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
