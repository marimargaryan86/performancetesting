<script lang="ts">
  import type { BeneficiaryData } from "$models/beneficiary-models/models";
  import CheckedIcon from "$src/lib/icons/checked-icon.svelte";
  import utils from "$src/lib/utils";
  import Navigation from "./navigation.svelte";

  export let data: Partial<BeneficiaryData>;
  export let goToNext: () => void;
  export let goToPrevious: () => void;
</script>

<div class="review">
  <div class="validation box">
    <CheckedIcon />
    Details validated succesfully
  </div>

  <section>
    <h3>Beneficiary Details</h3>

    <div class="data-table box">
      <strong>Type:</strong>
      <span>
        {data.type ? { individual: "Individual", company: "Company" }[data.type] : "N/A"}
      </span>

      {#if data.type === "individual"}
        <strong>First name:</strong>
        <span>{data.individualFirstName ?? "N/A"}</span>

        <strong>Last name:</strong>
        <span>{data.individualLastName ?? "N/A"}</span>

        <strong>Date of birth:</strong>
        <span>{data.individualBirthDate ? utils.formatDate(data.individualBirthDate) : "N/A"}</span>
      {:else if data.type === "company"}
        <strong>Company name:</strong>
        <span>{data.companyName}</span>

        <strong>Registration date:</strong>
        <span>
          {data.companyRegistrationDate ? utils.formatDate(data.companyRegistrationDate) : "N/A"}
        </span>
      {/if}

      <strong>Address:</strong>
      <span>{data.addressLine ?? "N/A"}</span>

      <strong>Postal code:</strong>
      <span>{data.addressPostalCode ?? "N/A"}</span>

      <strong>City:</strong>
      <span>{data.accountCity ?? "N/A"}</span>

      <strong>Country:</strong>
      <span>{data.addressCountry?.name ?? "N/A"}</span>
    </div>
  </section>

  <section>
    <h3>Bank details</h3>

    <div class="data-table box">
      <strong>Country:</strong>
      <span>{data.accountCountry?.name ?? "N/A"}</span>

      <strong>Currency:</strong>
      <span>{data.accountCurrency?.code ?? "N/A"}</span>

      <strong>Account holder name:</strong>
      <span>{data.accountHolderName ?? "N/A"}</span>

      <strong>Account number:</strong>
      <span>{data.accountNumber ?? "N/A"}</span>
    </div>
  </section>

  <section class="data-table">
    <h3>Options</h3>

    <div class="data-table box options">
      <strong>Priority</strong>
      {#if data.paymentTypes?.includes("priority")}
        <span>✓</span>
      {:else}
        <span>✖</span>
      {/if}

      <strong>Regular</strong>
      {#if data.paymentTypes?.includes("regular")}
        <span>✓</span>
      {:else}
        <span>✖</span>
      {/if}

      {#if data.paymentOptions?.includes("sort-code")}
        <strong>Sort code</strong>
        <span>{data.sortCode ?? "N/A"}</span>
      {/if}

      {#if data.paymentOptions?.includes("swift")}
        <strong>BIC/SWIFT</strong>
        <span>{data.bicSwift ?? "N/A"}</span>

        <strong>IBAN</strong>
        <span>{data.iban ?? "N/A"}</span>
      {/if}
    </div>
  </section>

  <Navigation {goToPrevious} {goToNext} />
</div>

<style>
  .review {
    display: grid;
    font-size: 16px;
    gap: 36px;
    grid-template-columns: 1fr 1fr;
  }

  section {
    grid-column: 1 / -1;
    width: 100%;
  }

  h3 {
    font-size: 24px;
    margin: 0 0 16px;
  }

  .box {
    background-color: var(--color-white);
    border-radius: 10px;
    padding: 24px;
    width: 100%;
  }

  .validation {
    align-items: center;
    display: flex;
    font-size: 24px;
    font-weight: 500;
    gap: 16px;
    grid-column: 1 / -1;
    padding: 19px 24px;
    vertical-align: middle;
  }

  .data-table {
    display: grid;
    grid-column: 1 / -1;
    grid-gap: 12px;
    grid-template-columns: 1fr 1fr;
    width: 100%;
  }

  .data-table > strong {
    font-weight: 600;
  }

  .data-table > span {
    color: var(--color-gray-light);
    font-weight: 400;
  }

  .review > :global(.navigation) {
    grid-column: 1 / -1;
  }
</style>
