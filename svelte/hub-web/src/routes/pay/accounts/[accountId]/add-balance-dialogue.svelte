<script lang="ts">
  import CloseIcon from "components/icons/close-icon.svelte";
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import SearchIcon from "components/icons/search-icon.svelte";
  import Button from "components/ui/button.svelte";
  import TextField from "components/ui/text-field.svelte";
  import { portal } from "directives/portal";
  import type { CurrencyAmount } from "models/currency";
  import { createEventDispatcher } from "svelte";
  import { fade, fly } from "svelte/transition";
  import { getRandomId } from "utils/random";

  export let balances: CurrencyAmount[];

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

  let value: CurrencyAmount[] = [];
  let searchQuery = "";
  let visible = false;
  let inputRef: TextField<"text">;

  const dispatch = createEventDispatcher<{ addbalances: CurrencyAmount[] }>();

  $: filteredBalances = balances.filter((item) =>
    item.code.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  function addBalances(): void {
    dispatch("addbalances", value);
    close();
  }
</script>

{#if visible}
  <div
    class="add-balance-dialogue"
    use:portal={document.body}
    transition:fade|local={{ duration: 200 }}
  >
    <div class="dialogue" transition:fly|local={{ duration: 200, y: 24 }} on:introend={focusSearch}>
      <div class="header">
        <h1>Add Balances</h1>

        <button on:click={close} class="close">
          <CloseIcon color="var(--color-neutral-700)" />
        </button>
      </div>

      <TextField
        type="text"
        bind:value={searchQuery}
        placeholder="Find a balance"
        bind:this={inputRef}
      >
        <SearchIcon slot="icon-before" color="var(--color-neutral-400)" />
      </TextField>

      <ul class="balances">
        {#each filteredBalances as balance}
          {@const id = getRandomId("balance")}
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
        <Button size="medium" variant="outline" on:click={close}>Cancel</Button>
        <Button size="medium" color="positive-gradient" on:click={addBalances}>Add</Button>
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
    background-color: rgb(237 248 245 / 0.5);
  }

  .dialogue {
    display: flex;
    flex-flow: column;
    gap: 16px;
    width: 100%;
    max-width: 480px;
    margin: 16px;
    padding: 16px 24px 24px;
    color: var(--color-neutral-800);
    background-color: rgb(255 255 255 / 0.6);
    border: var(--color-neutral-200) 1px solid;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.1);
    backdrop-filter: blur(25px);
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 700;
    font-size: 20px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 36px;
    letter-spacing: 1px;
  }

  .close {
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .close > :global(svg) {
    vertical-align: top;
  }

  .dialogue > :global(.text-field) {
    --height: 40px;
    --font-size: 12px;
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
    font-weight: 700;
    font-size: 16px;
    font-family: "Red Hat Display", Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 20px;
    letter-spacing: 0.1px;
    border: var(--color-neutral-200) 1px solid;
    border-radius: 8px;
    cursor: pointer;
  }

  .balance > :global(.currency-flag) {
    flex-shrink: 0;
  }

  input {
    display: none;
  }

  input:checked + .balance {
    border-color: var(--color-primary-500);
    box-shadow: 0 4px 20px rgb(0 0 0 / 0.1);
  }

  .actions {
    display: flex;
    gap: 16px;
    justify-content: flex-end;
  }

  .actions > :global(button) {
    width: 100%;
    max-width: 154px;
  }
</style>
