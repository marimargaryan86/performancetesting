<script lang="ts" context="module">
  export const LIST_BENEFICIARIES_LIMIT = 20;
</script>

<script lang="ts">
  import { capitalize } from "$lib/utils/common";
  import routeConfig from "$lib/route-config";
  import StandardLayout from "$lib/components/page/standard-layout.svelte";
  import { scrollLoad, type ScrollLoadFunc } from "$lib/directives/scroll-load";
  import integrationInstancesClient from "~/integration-instances-client";
  import currencyData from "~/data/currency-data";
  import { getPageTitle } from "$lib/utils/page-title";
  import Icon from "$lib/components/icons/icon.svelte";
  import { writable } from "svelte/store";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import { slideFade } from "$lib/transitions/slide-fade";

  export let data;

  $: beneficiaries = data.beneficiaries.data;

  const pending = writable(false);

  const loadMore: ScrollLoadFunc = async () => {
    if (!data.beneficiaries.cursor) {
      return { depleted: true };
    }

    const nextBeneficiaries = await integrationInstancesClient.hub.beneficiaries.find({
      cursor: data.beneficiaries.cursor,
      limit: LIST_BENEFICIARIES_LIMIT,
    });

    data.beneficiaries = {
      data: [...data.beneficiaries.data, ...nextBeneficiaries.data],
      cursor: nextBeneficiaries.cursor,
    };

    return { depleted: !nextBeneficiaries.cursor };
  };

  function remove(): void {
    if (!confirm("Are you sure you want to delete this beneficiary?")) {
      return;
    }
  }
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Pay", "Beneficiaries")}</title>
</svelte:head>

<StandardLayout pageTitle="Beneficiaries">
  <a
    variant="primary"
    size="small"
    href={routeConfig.routes.pay.routes.beneficiaries.routes.beneficiary().root}
    slot="actions"
  >
    Add Beneficiary
    <Icon variant="plus" size="20px" />
  </a>

  <x-table
    class="beneficiaries-table"
    use:scrollLoad={{ func: loadMore, pending }}
    style:grid-template-columns="2fr repeat(3, 1fr) min-content"
  >
    <x-thead>
      <x-th>Company</x-th>
      <x-th>Currency</x-th>
      <x-th>Bank Country</x-th>
      <x-th>Type</x-th>
      <x-th />
    </x-thead>

    {#each beneficiaries as item (item.id)}
      {@const currency = currencyData.mapping[item.currencyId]}

      <x-tr>
        <x-td class="company-name">{item.bankAccountHolderName}</x-td>
        <x-td class="currency">
          <strong typography="body-medium" weight="bold">{item.currencyId}</strong>
          <span typography="body-small">{currency?.name ?? ""}</span>
        </x-td>
        <x-td>{item.bankDetails.address.countryCode}</x-td>
        <x-td>{capitalize(item.bankDetails.paymentType)}</x-td>
        <x-tactions>
          <a
            href={routeConfig.routes.pay.routes.beneficiaries.routes.beneficiary(item.id).root}
            class="action"
          >
            <Icon variant="edit" size="32px" />
          </a>

          <button on:click={remove.bind(remove)} class="action">
            <Icon variant="remove-trash" size="32px" />
          </button>

          <button class="outline action" typography="body-medium" weight="bold">Pay</button>
        </x-tactions>
      </x-tr>
    {/each}

    {#if $pending}
      <x-tloading transition:slideFade={{ duration: 200 }}>
        <LoadingIcon color="var(--color-main-primary-500)" />
      </x-tloading>
    {/if}
  </x-table>
</StandardLayout>

<style>
  .beneficiaries-table {
    height: 100%;
  }

  .currency {
    display: flex;
    flex-flow: column;
    padding-top: 8px;
    padding-bottom: 8px;
  }

  .currency > span {
    color: var(--color-common-light-soft);
  }

  x-tr:hover .company-name {
    color: var(--color-common-light-text-link);
  }

  .action {
    padding: 0;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .action.outline {
    padding: 6px 16px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
  }

  .action > :global(.icon) {
    vertical-align: top;
  }
</style>
