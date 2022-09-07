<script lang="ts">
  import type { BeneficiaryModel } from "$integration/currency-cloud/models/beneficiaries/common";
  import Table from "$lib/components/table.svelte";
  import DeleteIcon from "$lib/icons/delete-icon.svelte";
  import EditIcon from "$lib/icons/edit-icon.svelte";
  import instances from "$services/instances";
  import { onMount } from "svelte";
  import { currencyStore } from "$lib/stores";
  import type { CurrencyModel } from "$integration/currency-cloud/models/currencies";
  import routeConfig from "$lib/route-config";
  import { flip } from "svelte/animate";
  import Button from "$lib/components/button.svelte";

  let currencies: CurrencyModel[] = [];
  let beneficiaries: BeneficiaryModel[] = [];
  let offset = 0;
  let pending = false;
  let depleted = false;

  const limit = 20;
  // TODO: Right now, nicknames that don't begin with an alphanumeric won't be displayed.
  const groups = [..."0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("")];

  $: alphaGroups = groups.map((char) => ({
    id: char,
    beneficiaries: beneficiaries.filter((item) =>
      item.nickname.toLocaleLowerCase().startsWith(char.toLocaleLowerCase()),
    ),
  }));

  async function deleteBeneficiary(id: string) {
    if (!confirm("Are you sure you want to delete beneficiary?")) {
      return;
    }

    try {
      await instances.beneficiary.remove(id);

      beneficiaries = beneficiaries.filter((item) => item.id !== id);
    } catch {
      //
    }
  }

  function editBeneficiary(id: string) {
    alert(id);
  }

  async function loadMore(): Promise<void> {
    if (pending) {
      return;
    }

    try {
      pending = true;
      const nextBeneficiaries = await instances.beneficiary.find({ offset, limit });
      offset++;

      depleted = !nextBeneficiaries.length;
      beneficiaries = [...beneficiaries, ...nextBeneficiaries];
    } finally {
      pending = false;
    }
  }

  onMount(async () => {
    loadMore();

    currencies = await $currencyStore;
  });
</script>

<div class="beneficiary-list">
  <Table>
    <thead>
      <tr>
        <th>Beneficiary</th>
        <th>Currency</th>
        <th>Type</th>
        <th>Bank Country</th>
        <th>Payment types</th>
        <th>Actions</th>
      </tr>
    </thead>

    {#each alphaGroups as alphaGroup}
      {#if alphaGroup.beneficiaries.length}
        <tbody>
          <h3>{alphaGroup.id.toUpperCase()}</h3>
          {#each alphaGroup.beneficiaries as beneficiary (beneficiary.id)}
            <tr animate:flip={{ duration: 200 }}>
              <td>{beneficiary.nickname}</td>
              <td>
                <img
                  class="currency-flag"
                  src="/images/currency-flags/{beneficiary.bank.account.currencyCode.toLocaleLowerCase()}.png"
                  alt=""
                />

                {currencies.find((item) => item.code === beneficiary.bank.account.currencyCode)
                  ?.name}

                ({beneficiary.bank.account.currencyCode})
              </td>
              <td>{beneficiary.entityType ?? "-"}</td>
              <td>{beneficiary.bank.countryCode}</td>
              <td>{beneficiary.paymentTypes.join(", ")}</td>
              <td>
                <a class="action" href={routeConfig.pay}>Pay</a>

                <button
                  class="action"
                  on:click={() => editBeneficiary(beneficiary.id)}
                  title="Edit"
                >
                  <EditIcon />
                </button>

                <button
                  class="action"
                  on:click={() => deleteBeneficiary(beneficiary.id)}
                  title="Delete"
                >
                  <DeleteIcon />
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      {/if}
    {/each}
  </Table>

  {#if !(pending || depleted)}
    <Button on:click={loadMore}>Load more</Button>
  {/if}
</div>

<style>
  .beneficiary-list {
    margin-top: 56px;
  }

  .beneficiary-list > :global(table) {
    width: 100%;
  }

  h3 {
    font-size: 25px;
    font-weight: 400;
    margin: 16px 0;
    padding-left: 16px;
  }

  th {
    color: var(--color-gray-darkest);
  }

  td {
    padding: 12px 16px;
  }

  tbody > tr:first-of-type > td:first-of-type {
    border-top-left-radius: 10px;
  }

  tbody > tr:first-of-type > td:last-of-type {
    border-top-right-radius: 10px;
  }

  .currency-flag {
    border: var(--color-gray-lighter) 1px solid;
    border-radius: 3px;
    margin-right: 8px;
    vertical-align: middle;
    width: 30px;
  }

  .action {
    background-color: transparent;
    border: 0;
    color: var(--color-orange);
    cursor: pointer;
    display: inline-block;
    font-size: 14px;
    font-weight: 400;
    margin: 0 2px;
    vertical-align: middle;
  }

  .beneficiary-list > :global(button) {
    background-color: var(--color-orange);
    display: block;
    margin: 24px auto;
  }
</style>
