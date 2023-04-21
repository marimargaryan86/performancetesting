<script lang="ts">
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { portal } from "directives/portal";
  import integrationInstances from "integration-instances";
  import type { CurrencyModel, MoneyModel } from "models/money";
  import { createEventDispatcher, onMount } from "svelte";
  import { fade, fly } from "svelte/transition";

  export let token: string | undefined;
  export let accountId: string;
  export let exclude: MoneyModel[];

  let balances: CurrencyModel[] = [];

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

  const dispatch = createEventDispatcher<{ addbalances: MoneyModel[] }>();

  $: filteredBalances = balances.filter(
    (balance) =>
      balance.code.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !exclude.find((money) => money.currency === balance.code),
  );

  async function addBalances(): Promise<void> {
    if (!token) {
      close();

      return;
    }

    const nextBalances = await Promise.all(
      value.map((item) =>
        integrationInstances.junctionPay.balances.addBalance(token as string, accountId, item.code),
      ),
    );

    dispatch("addbalances", nextBalances);
    close();
  }

  onMount(() => {
    (async (): Promise<void> => {
      if (!token) {
        return;
      }

      balances = await integrationInstances.junctionPay.currencies.listCurrencies(token);
    })();
  });
</script>

{#if visible}
  <div
    class="add-balance-dialogue"
    use:portal={document.body}
    transition:fade|local={{ duration: 200 }}
  >
    <div class="dialogue" transition:fly|local={{ duration: 200, y: 24 }} on:introend={focusSearch}>
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
        <button on:click={close} class="typography body-large bold">Cancel</button>
        <button on:click={addBalances} class="typography body-large bold">Add</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .add-balance-dialogue {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100vh;
    background-color: rgb(140 142 146 / 0.5);
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
    backdrop-filter: blur(25px);
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

  .actions > button {
    flex-grow: 1;
    height: 48px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: var(--color-main-primary-500) 1px solid;
    border-radius: 8px;
    cursor: pointer;
  }

  .actions > button:last-child {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
  }
</style>
