<script lang="ts">
  import balanceAccounts from "$content/balance-accounts";
  import Button from "$lib/components/button.svelte";
  import SelectField from "$lib/components/select-field.svelte";
  import Table from "$lib/components/table.svelte";
  import DownloadIcon from "$lib/icons/download-icon.svelte";
  import routeConfig from "$lib/route-config";
  import utils from "$lib/utils";
  import Layout from "../_layout.svelte";

  const accounts = balanceAccounts;

  const currencies = [
    { code: "USD" },
    { code: "GBP" },
    { code: "EUR" },
    { code: "AED" },
    { code: "AUD" },
  ].map((currency) => ({ ...currency, toString: () => currency.code }));
  let currency: { code: string } | undefined = undefined;
</script>

<svelte:head>
  <title>Junction | Sub Accounts</title>
</svelte:head>

<Layout>
  <div class="select-currency" slot="action">
    <SelectField bind:value={currency} items={currencies} placeholder="Choose Currencies" />

    <Button>
      <DownloadIcon />
    </Button>
  </div>

  <div class="sub-accounts" slot="body">
    <Table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Ref</th>
          <th>USD Balance</th>
          <th>GBP Balance</th>
          <th>EUR Balance</th>
          <th>AED Balance</th>
          <th>AUD Balance</th>
          <th />
        </tr>
      </thead>

      <tbody>
        {#each accounts as account}
          <tr>
            <td>{account.id.substring(0, 8)}...</td>
            <td>{account.name}</td>
            <td>{account.ref}</td>
            <td>{utils.formatCurrency(account.USD)}</td>
            <td>{utils.formatCurrency(account.GBP)}</td>
            <td>{utils.formatCurrency(account.EUR)}</td>
            <td>{utils.formatCurrency(account.AED)}</td>
            <td>{utils.formatCurrency(account.AUD)}</td>
            <td class="view"><a href={routeConfig.balances.subAccount(account.id)}>View</a></td>
          </tr>
        {/each}

        <tr class="totals">
          <td>Totals</td>
          <td />
          <td />
          <td>{utils.formatCurrency(accounts.reduce((prev, curr) => prev + curr.USD, 0))}</td>
          <td>{utils.formatCurrency(accounts.reduce((prev, curr) => prev + curr.GBP, 0))}</td>
          <td>{utils.formatCurrency(accounts.reduce((prev, curr) => prev + curr.EUR, 0))}</td>
          <td>{utils.formatCurrency(accounts.reduce((prev, curr) => prev + curr.AED, 0))}</td>
          <td>{utils.formatCurrency(accounts.reduce((prev, curr) => prev + curr.AUD, 0))}</td>
          <td />
        </tr>
      </tbody>
    </Table>
  </div>
</Layout>

<style>
  .select-currency {
    align-items: center;
    display: flex;
    gap: 8px;
  }

  .select-currency > :global(button) {
    background-color: transparent;
    height: 100%;
  }

  .sub-accounts {
    padding: 0 49px 30px;
  }

  .sub-accounts > :global(table) {
    width: 100%;
  }

  .select-currency > :global(.select-field.select-field) {
    border-color: transparent;
    border-radius: 0;
    height: 100%;
    width: 388px;
  }

  .totals {
    font-weight: 700;
  }

  a {
    color: var(--color-orange);
    font-size: 12px;
    font-weight: 500;
    text-decoration: none;
  }

  a::after {
    border: var(--color-orange) 1px solid;
    border-width: 1px 1px 0 0;
    content: "";
    display: inline-block;
    height: 6px;
    margin-left: 5px;
    transform: translateY(-1px) rotateZ(45deg);
    width: 6px;
  }

  .view {
    white-space: nowrap;
  }
</style>
