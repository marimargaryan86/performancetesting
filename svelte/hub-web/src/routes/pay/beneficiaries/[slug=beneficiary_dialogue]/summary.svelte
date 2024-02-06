<script lang="ts">
  import { capitalize } from "~/utils/common";
  import type { BeneficiaryPut } from "~/integration/junction-hub-api/schemas/beneficiary";
  import integrationInstancesClient from "~/integration-instances-client";
  import countryData from "~/data/country-data";
  import currencyData from "~/data/currency-data";

  export let data: BeneficiaryPut;
  export let error: string | undefined = undefined;

  $: currency = currencyData.mapping[data.currencyId];
  $: beneficiaryCountry = data.address?.countryCode
    ? countryData.mapping[data.address.countryCode]
    : undefined;
  $: bankCountry = data.bankDetails.address?.countryCode
    ? countryData.mapping[data.bankDetails.address.countryCode]
    : undefined;

  export async function validate(): Promise<boolean> {
    error = undefined;

    try {
      if (data.id) {
        await integrationInstancesClient.hub.beneficiaries.update({ data, id: data.id });
      } else {
        await integrationInstancesClient.hub.beneficiaries.create({ data });
      }

      return true;
    } catch {
      return false;
    }
  }
</script>

<div class="summary">
  <h2 typography="headline-small" weight="bold">Summary</h2>

  <div class="section">
    <h3 typography="title-medium" weight="bold">Beneficiary Details</h3>
    <div class="table" typography="body-medium">
      <strong>Personalised name:</strong>
      <span>{data.account?.company?.id ?? "-"}</span>
      <strong>Email:</strong>
      <span>{data.email ?? "-"}</span>
      <strong>Address:</strong>
      <span
        >{data.address.street.line1}
        {data.address.street.line2 ?? ""}</span
      >
      <strong>City:</strong>
      <span>{data.address?.city ?? "-"}</span>
      <strong>Postcode:</strong>
      <span>{data.address?.postalCode ?? "-"}</span>
      <strong>State:</strong>
      <span>{data.address?.state ?? "-"}</span>
      <strong>Country:</strong>
      <span>
        {beneficiaryCountry ? `${beneficiaryCountry.name} (${beneficiaryCountry.code})` : "-"}
      </span>
    </div>
  </div>

  <div class="section">
    <h3 typography="title-medium" weight="bold">Bank Account Details</h3>
    <div class="table" typography="body-medium">
      <strong>Bank Name:</strong>
      <span>{data.bankDetails.name ?? "-"}</span>
      <strong>Bank Address:</strong>
      <span
        >{data.bankDetails.address.street.line1} {data.bankDetails.address.street.line2 ?? ""}</span
      >
      <strong>Country:</strong>
      <span>
        {bankCountry ? `${bankCountry.name} (${bankCountry.code})` : "-"}
      </span>
      <strong>Currency:</strong>
      <span>{currency ? `${currency.name} (${currency.code})` : "-"}</span>

      <hr />
      <h4 typography="body-medium" weight="bold">
        {capitalize(data.bankDetails.paymentType ?? "")} Payment
      </h4>

      <strong>BIC/SWIFT:</strong>
      <span>{data.bankDetails.bicSwift ?? "-"}</span>

      {#if data.bankDetails.type === "aba"}
        <strong>Sort Code:</strong>
        <span>{data.bankDetails.aba ?? "-"}</span>
        <strong>Account Number:</strong>
        <span>{data.bankDetails.accountNumber ?? "-"}</span>
      {:else}
        <strong>IBAN Code:</strong>
        <span>{data.bankDetails.iban ?? "-"}</span>
      {/if}
    </div>
  </div>
</div>

<style>
  .summary {
    display: flex;
    flex-flow: column;
    gap: 40px;
    align-self: center;
    width: 100%;
    max-width: 914px;
    color: var(--color-common-light-strong);
  }

  .section {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .table {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 8px;
    padding: 24px;
    border: var(--color-main-neutral-50) 1px solid;
    border-radius: 16px;
  }

  hr,
  h4 {
    grid-column: 1 / -1;
  }

  hr {
    margin: 24px 0;
    border: 0;
    border-bottom: var(--color-common-line-soft) 1px solid;
  }

  h4 {
    margin: 0 0 16px;
  }

  strong {
    color: var(--color-common-light-medium);
  }

  span {
    font-weight: 600;
  }
</style>
