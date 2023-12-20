<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import CurrencyFlag from "components/icons/currency-flag.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import { formatAmount } from "formatting/currency";
  import AddBalanceDialogue from "./add-balance-dialogue.svelte";
  import Button from "components/ui/button.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import routeConfig from "routeConfig";
  import type { Balance } from "integration/junction-hub-api/schemas/balance";
  import { getPageTitle } from "utils/page-title";
  import { getLocaleData } from "i18n";

  export let data;

  const i18n = getLocaleData();

  let searchQuery = "";
  let dialogue: AddBalanceDialogue;

  $: breadCrumbs = [
    { url: routeConfig.routes.pay.routes.accounts.root, label: "Accounts" },
    {
      url: routeConfig.routes.pay.routes.accounts.routes.account(data.account.id).root,
      label: data.account.name,
    },
  ];
  $: balances = data.balances
    .filter((item) => item.currencyId.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => 0 - (a.currencyId < b.currencyId ? 1 : -1));

  function openDialogue(): void {
    dialogue.open();
  }

  function addBalances(event: CustomEvent<Balance[]>): void {
    data.balances = [...event.detail, ...data.balances];
  }
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $i18n.title,
      $i18n.pages.pay.title,
      $i18n.pages.pay.pages.accounts.title,
      data.account.name,
      $i18n.words.balances,
    )}
  </title>
</svelte:head>

<AddBalanceDialogue
  exclude={balances}
  accountId={data.account.id}
  on:addbalances={addBalances}
  bind:this={dialogue}
/>

<StandardLayout pageTitle={$i18n.words.balances} {breadCrumbs} bind:searchQuery>
  <Button size="small" on:click={openDialogue} slot="actions">
    {$i18n.actions.addBalance}
    <PlusIcon />
  </Button>

  <ul class="balances">
    {#each balances as balance}
      <li>
        <a href="#top" class="balance">
          <CurrencyFlag code={balance.currencyId} />

          <span>
            <strong class="typography body-large bold">
              {formatAmount({ currency: balance.currencyId, amount: balance.amount })}
            </strong>
            <span class="typography body-small">{balance.currency}</span>
          </span>

          <ChevronIcon color="var(--color-main-neutral-700)" size="20px" />
        </a>
      </li>
    {:else}
      <li class="typography body-large empty">{$i18n.sentences.noBalancesFound}</li>
    {/each}
  </ul>
</StandardLayout>

<style>
  .balances {
    display: flex;
    flex-flow: column;
    gap: 8px;
    height: 100%;
    padding: 32px 40px;
    overflow-y: auto;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .balance {
    display: flex;
    gap: 24px;
    align-items: center;
    height: 60px;
    padding: 16px;
    text-decoration: none;
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-100) 1px solid;
    border-radius: 8px;
  }

  .balance > span {
    display: flex;
    flex-grow: 1;
    gap: 8px;
    align-items: center;
    color: var(--color-main-neutral-800);
  }

  .balance > :global(.currency-flag),
  .balance > :global(.chevron-icon) {
    flex-shrink: 0;
  }

  .empty {
    color: var(--color-main-neutral-600);
  }
</style>
