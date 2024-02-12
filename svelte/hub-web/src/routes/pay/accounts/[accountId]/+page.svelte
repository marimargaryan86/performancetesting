<script lang="ts">
  import ChevronIcon from "$lib/components/icons/chevron-icon.svelte";
  import CurrencyFlag from "$lib/components/icons/currency-flag.svelte";
  import { formatAmount } from "$lib/formatting/currency";
  import AddBalanceDialogue from "$lib/components/pages/pay/accounts/add-balance-dialogue.svelte";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import routeConfig from "$lib/route-config";
  import { getPageTitle } from "$lib/utils/page-title";
  import { getLocale, getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";
  import type { ComponentEvents } from "svelte";

  export let data;

  const locale = getLocale();
  const t = getTranslator();

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

  function addBalances(event: ComponentEvents<AddBalanceDialogue>["addbalances"]): void {
    data.balances = [...event.detail, ...data.balances];
  }
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.pay.title"),
      $t("pages.pay.pages.accounts.title"),
      data.account.name,
      $t("words.balances"),
    )}
  </title>
</svelte:head>

<AddBalanceDialogue
  exclude={balances}
  accountId={data.account.id}
  on:addbalances={addBalances}
  bind:this={dialogue}
/>

<StandardLayout pageTitle={$t("words.balances")} {breadCrumbs} bind:searchQuery>
  <button variant="primary" size="small" on:click={openDialogue} slot="actions">
    {$t("actions.addBalance")}
    <Icon variant="plus" size="20px" />
  </button>

  <ul class="balances">
    {#each balances as balance}
      <li>
        <a href="#top" class="balance">
          <CurrencyFlag code={balance.currencyId} />

          <span>
            <strong typography="body-large" weight="bold">
              {formatAmount({ currency: balance.currencyId, amount: balance.amount }, $locale)}
            </strong>
            <span typography="body-small">{balance.currency}</span>
          </span>

          <ChevronIcon color="var(--color-main-neutral-700)" size="20px" />
        </a>
      </li>
    {:else}
      <li typography="body-large" class="empty">{$t("sentences.noBalancesFound")}</li>
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
