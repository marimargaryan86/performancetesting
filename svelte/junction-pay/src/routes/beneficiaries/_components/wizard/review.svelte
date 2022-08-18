<script lang="ts">
  import { wizardStore } from "$lib/stores";
  import Navigation from "./navigation.svelte";

  export let goToNext: () => void;
  export let goToPrevious: () => void;

  $: wizard = $wizardStore;
</script>

<div class="review">
  <div class="header">
    <div class="section">Details validated succesfully</div>
  </div>
  <div class="details">
    <h4>Beneficiary Details</h4>
    <div class="section">
      <div class="label">Address</div>
      <div class="value">{wizard.addressLine}</div>
      <div class="label">Country</div>
      <div class="value">{wizard.beneficiaryCountry?.name}</div>
    </div>
  </div>
  <div class="bank">
    <h4>Beneficiary Bank Details</h4>
    <div class="section">
      <div class="label">Currency</div>
      <div class="value">{wizard.currency}</div>
    </div>
  </div>
  <div class="priority">
    <div class="section">
      <div class="label">Beneficiary type</div>
      <div class="value">{wizard.beneficiaryEntityType}</div>
      <div class="label">Address</div>
      <div class="value">{wizard.addressLine}</div>
      <div class="label">Post code</div>
      <div class="value">{wizard.postCode}</div>
      <!-- Change for company if statement -->
      {#if wizard.beneficiaryEntityType === "individual"}
        <div class="label">First name</div>
        <div class="value">{wizard.beneficiaryLastName}</div>
        <div class="label">Last name</div>
        <div class="value">{wizard.beneficiaryLastName}</div>
      {:else if wizard.beneficiaryEntityType === "company"}
        <div class="label">First name</div>
        <div class="value">{wizard.beneficiaryEntityName}</div>
      {/if}

      <div class="label">Sort code</div>
      <div class="value">{wizard.sortCode}</div>
      <div class="label">Account Number</div>
      <div class="value">{wizard.accountNumber}</div>
    </div>
  </div>
  <div class="regular">
    <div class="section">
      <div class="label">Beneficiary type</div>
      <div class="value">{wizard.beneficiaryEntityType}</div>
      <div class="label">Sort code</div>
      <div class="value">{wizard.sortCode}</div>
      <div class="label">Account number</div>
      <div class="value">{wizard.accountNumber}</div>
      <div class="label">Country</div>
      <div class="value">{wizard.beneficiaryCountry?.name}</div>
    </div>
  </div>
  <div class="bank-info">
    <div class="section">
      <div class="wrapper">
        <div class="label">Bank name</div>
        <div class="value">Test bank</div>
        <div class="label">Bank address</div>
        <div class="value">123 Bank Street</div>
      </div>
    </div>
  </div>
</div>
<Navigation goToNext={() => goToNext()} {goToPrevious} />

<style>
  h4 {
    font-size: 24px;
    margin: 16px 0 24px;
  }

  .review {
    column-gap: 16px;
    display: grid;
    gap: 16px;
    grid-template-columns: 1fr 1fr;
  }

  .header {
    grid-column: 1 / 3;
  }

  .details {
    grid-column: 1 / 3;
  }

  .bank {
    grid-column: 1 / 3;
  }

  .priority {
    grid-column: 1/ 2;
  }

  .bank-info {
    grid-column: 1/ 3;
  }

  .section {
    background-color: white;
    border-radius: 8px;
    display: grid;
    gap: 12px;
    grid-template-columns: 1fr 1fr;
    margin: 8px 0;
    padding: 24px;
  }

  .wrapper {
    width: 50%;
  }

  .bank-info .section {
    display: flex;
  }

  .bank-info .section .wrapper {
    display: grid;
    gap: 12px;
    grid-template-columns: 1fr 1fr;
    width: 46.5%;
  }

  .priority .section,
  .regular .section {
    height: 100%;
  }

  .value {
    color: var(--color-grey-text);
  }
</style>
