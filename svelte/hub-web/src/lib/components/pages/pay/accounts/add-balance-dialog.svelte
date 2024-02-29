<script lang="ts">
  import CurrencyFlag from "$lib/components/icons/currency-flag.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import TextField from "$lib/components/ui/text-field.svelte";
  import { portal } from "$lib/directives/portal";
  import { createEventDispatcher } from "svelte";
  import { fade, fly } from "svelte/transition";
  import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
  import integrationInstancesClient from "~/integration-instances-client";
  import currencyData from "~/data/currency-data";
  import { writable } from "svelte/store";
  import { getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";

  export let accountId: string;
  export let exclude: HubSchemas.Balance[];

  const t = getTranslator();

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

  let value: HubSchemas.Currency[] = [];
  let searchQuery = "";
  let visible = false;
  let inputRef: TextField<"text">;

  const dispatch = createEventDispatcher<{ addbalances: HubSchemas.Balance[] }>();
  const pending = writable(false);

  $: filteredBalances = currencyData.list.filter(
    (balance) =>
      balance.code.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !exclude.find((money) => money.currencyId === balance.code),
  );

  async function addBalances(): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;

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
    } finally {
      $pending = false;
    }
  }
</script>

{#if visible}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->

  <div
    class="add-balance-dialog"
    on:click|self={close}
    use:portal={document.body}
    transition:fade={{ duration: 200 }}
  >
    <div class="dialog" transition:fly={{ duration: 200, y: 24 }} on:introend={focusSearch}>
      <h1 typography="headline-medium" weight="bold">{$t("actions.addBalances")}</h1>

      <TextField
        type="text"
        bind:value={searchQuery}
        placeholder={$t("sentences.findABalance")}
        bind:this={inputRef}
      >
        <Icon
          variant="search"
          size="20px"
          slot="icon-before"
          color="var(--color-main-neutral-400)"
        />
      </TextField>

      <ul class="balances" typography="body-large" weight="bold">
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
        <button on:click={close} variant="outline" size="medium">{$t("actions.cancel")}</button>
        <button on:click={addBalances} variant="primary" size="medium" disabled={!value.length}>
          {$t("actions.add")}

          {#if $pending}
            <LoadingIcon />
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .add-balance-dialog {
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

  .dialog {
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

  .dialog > :global(.text-field) {
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
  }
</style>
