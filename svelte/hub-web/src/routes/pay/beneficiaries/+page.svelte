<script lang="ts">
  import Header from "components/ui/table/header.svelte";
  import TBody from "components/ui/table/t-body.svelte";
  import TCol from "components/ui/table/t-col.svelte";
  import THead from "components/ui/table/t-head.svelte";
  import TRow from "components/ui/table/t-row.svelte";
  import Table from "components/ui/table/table.svelte";
  import { callAction, capitalize, type FlattenedObject } from "utils/common";
  import type { DirectionY } from "models/spatial";
  import SearchField from "components/ui/search-field.svelte";
  import Button from "components/ui/button.svelte";
  import PlusIcon from "components/icons/plus-icon.svelte";
  import type { BeneficiaryModel } from "models/beneficiary";
  import EditIcon from "components/icons/edit-icon.svelte";
  import RemoveIcon from "components/icons/remove-icon.svelte";
  import routeConfig from "routeConfig";

  export let data;
  export let form;

  let sortGroup: FlattenedObject<BeneficiaryModel> = "name";
  let sortDirection: DirectionY = "down";
  let searchQuery = "";

  $: beneficiaries = data.beneficiaries.data;

  async function loadMore(): Promise<void> {
    if (!data.beneficiaries.cursor) {
      return;
    }

    await callAction(routeConfig.pay.beneficiaries.actions.listBeneficiaries, {
      cursor: data.beneficiaries.cursor,
    });

    if (form?.beneficiaries) {
      data.beneficiaries = {
        cursor: form.beneficiaries.cursor,
        data: [...data.beneficiaries.data, ...form.beneficiaries.data],
      };
    }
  }

  function createRemoveFunc(): () => void {
    return () => {
      if (!confirm("Are you sure you want to delete this beneficiary?")) {
        return;
      }
    };
  }
</script>

<svelte:head>
  <title>Beneficiaries · Pay · Junction Hub</title>
</svelte:head>

<div class="header">
  <h1 class="typography headline-medium bold">Beneficiaries</h1>

  <div class="actions">
    <SearchField bind:value={searchQuery} />

    <Button size="small" href={routeConfig.pay.beneficiaries.addBeneficiary}>
      Add Beneficiary
      <PlusIcon />
    </Button>
  </div>
</div>

<div class="content">
  <Table class="beneficiaries-table" {loadMore}>
    <THead>
      <Header bind:sortGroup bind:sortDirection sortValue="name">Company</Header>
      <Header>Currency</Header>
      <Header bind:sortGroup bind:sortDirection sortValue="countryName">Bank Country</Header>
      <Header>Type</Header>
      <Header />
    </THead>

    <TBody>
      {#each beneficiaries as item (item.id)}
        <TRow alternatingBackground={false}>
          <TCol class="company-name typography body-medium bold">{item.name}</TCol>
          <TCol>
            <div class="currency">
              <strong class="typography body-medium bold">{item.currency.code}</strong>
              <span class="typography body-small">{item.currency.name}</span>
            </div>
          </TCol>
          <TCol class="typography body-medium bold">{item.countryName}</TCol>
          <TCol class="typography body-medium">{capitalize(item.type)}</TCol>
          <TCol width="172px">
            <div class="beneficiary-actions">
              <a href={routeConfig.pay.beneficiaries.beneficiary(item.id)}><EditIcon /></a>

              <button on:click={createRemoveFunc()}>
                <RemoveIcon variant="trash-can" />
              </button>

              <button class="outline typography body-medium bold">Pay</button>
            </div>
          </TCol>
        </TRow>
      {/each}
    </TBody>
  </Table>
</div>

<style>
  .content > :global(.table.beneficiaries-table) {
    width: 100%;
    height: 100%;
    color: var(--color-common-light-strong);
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32px 24px;
    color: var(--color-main-neutral-800);
  }

  .actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }

  .currency {
    display: flex;
    flex-flow: column;
  }

  .currency > span {
    color: var(--color-common-light-soft);
  }

  .beneficiary-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    opacity: 0;
    pointer-events: 0;
  }

  .content :global(tr:hover .beneficiary-actions) {
    opacity: 1;
    pointer-events: all;
  }

  .content :global(tr:hover .company-name) {
    color: var(--color-common-light-text-link);
  }

  .beneficiary-actions > button,
  .beneficiary-actions > a {
    padding: 0;
    text-decoration: none;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  .beneficiary-actions > .outline {
    padding: 6px 16px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 8px;
  }

  .beneficiary-actions > button > :global(svg),
  .beneficiary-actions > a > :global(svg) {
    vertical-align: top;
  }
</style>
