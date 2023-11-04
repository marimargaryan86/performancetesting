<script lang="ts" context="module">
  export const LIST_BENEFICIARIES_LIMIT = 20;
</script>

<script lang="ts">
  import { dev } from "$app/environment";
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import { capitalize } from "utils/common";
  import Button from "components/ui/button.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import EditIcon from "components/icons/edit-icon.svelte";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import routeConfig from "routeConfig";
  import TActionsCol from "components/ui/table/t-actions-col.svelte";
  import StandardLayout from "components/page/standard-layout.svelte";
  import type { ScrollLoadFunc } from "directives/scroll-load";
  import integrationInstancesClient from "integration-instances-client";

  export let data;

  $: beneficiaries = data.beneficiaries.data;

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
  <title>Beneficiaries · Pay · Junction Hub</title>
</svelte:head>

{#if !dev}
  <div />
{:else}
  <StandardLayout pageTitle="Beneficiaries">
    <Button
      size="small"
      href={routeConfig.routes.pay.routes.beneficiaries.routes.beneficiary().root}
      preload={false}
      slot="actions"
    >
      Add Beneficiary
      <PlusIcon />
    </Button>

    <Table class="beneficiaries-table" {loadMore}>
      <THead>
        <Header>Company</Header>
        <Header>Currency</Header>
        <Header>Bank Country</Header>
        <Header>Type</Header>
        <Header />
      </THead>

      <TBody>
        {#each beneficiaries as item (item.id)}
          {@const currency = data.currencies.get(item.currencyId)}

          <TRow alternatingBackground={false}>
            <TCol class="company-name typography body-medium bold">
              {item.bankAccountHolderName}
            </TCol>
            <TCol>
              <div class="currency">
                <strong class="typography body-medium bold">{item.currencyId}</strong>
                <span class="typography body-small">{currency?.name ?? ""}</span>
              </div>
            </TCol>
            <TCol class="typography body-medium bold">{item.bankDetails.address.countryCode}</TCol>
            <TCol class="typography body-medium">{capitalize(item.bankDetails.paymentType)}</TCol>
            <TActionsCol>
              <a
                href={routeConfig.routes.pay.routes.beneficiaries.routes.beneficiary(item.id).root}
                data-sveltekit-preload-data="off"
                class="action"
              >
                <EditIcon />
              </a>

              <button on:click={remove.bind(remove)} class="action">
                <RemoveIcon variant="trash-can" />
              </button>

              <button class="outline action typography body-medium bold">Pay</button>
            </TActionsCol>
          </TRow>
        {/each}
      </TBody>
    </Table>
  </StandardLayout>
{/if}

<style>
  :global(.table.beneficiaries-table) {
    width: 100%;
    height: 100%;
    color: var(--color-common-light-strong);
  }

  .currency {
    display: flex;
    flex-flow: column;
  }

  .currency > span {
    color: var(--color-common-light-soft);
  }

  :global(tr:hover .company-name) {
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

  .action > :global(svg) {
    vertical-align: top;
  }
</style>
