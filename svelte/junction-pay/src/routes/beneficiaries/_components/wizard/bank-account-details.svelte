<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import Radio from "$lib/components/radio.svelte";
  import Spinner from "$lib/components/spinner.svelte";
  import utils from "$lib/utils";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";
  import instances from "$services/instances";
  import { scale } from "svelte/transition";
  import Navigation from "./navigation.svelte";
  import AccountDetails from "./_components/account-details.svelte";
  import CompanyDetails from "./_components/company-details.svelte";
  import IndividualDetails from "./_components/individual-details.svelte";
  import PaymentOptions from "./_components/payment-options.svelte";
  import PaymentTypes from "./_components/payment-types.svelte";

  export let goToNext: () => void;
  export let goToPrevious: () => void;

  let errors: ValidationError<AddBeneficiaryBankDetailsCombined> = {};

  const data: Partial<AddBeneficiaryBankDetailsCombined> = {
    beneficiaryEntityType: "company",
    beneficiaryDateOfBirth: undefined,
    paymentTypes: [],
    options: [],
    beneficiaryEntityName: "",
  };

  const { beneficiary: service } = instances;
  const { pending, func: addBeneficiaryBankDetails } = utils.pendableCall(
    service.addBeneficiaryBankDetails.bind(service),
    false,
  );

  async function submit(): Promise<void> {
    if ($pending) {
      return;
    }
    errors = {};

    try {
      await addBeneficiaryBankDetails(data as AddBeneficiaryBankDetailsCombined);
      goToNext();
    } catch (e) {
      errors = e as typeof errors;
    }
  }
</script>

<div class="bank-account-details">
  <form class="beneficiary-bank-details" on:submit|preventDefault={submit}>
    <fieldset class="beneficiary-type">
      <legend>Beneficiary type</legend>
      <p>Select the type of beneficiary you want to create</p>
      <div class="radio-container">
        <Radio value="company" bind:group={data.beneficiaryEntityType} id="company" />
        <label for="company">Company</label>

        <Radio value="individual" bind:group={data.beneficiaryEntityType} id="individual" />
        <label for="individual">Individual</label>
      </div>
    </fieldset>
    {#if data.beneficiaryEntityType === "company"}
      <CompanyDetails {errors} {data} />
    {:else if data.beneficiaryEntityType === "individual"}
      <IndividualDetails {errors} {data} />
    {/if}
    {#if data.beneficiaryEntityType !== undefined}
      <legend class="subtitle">Account Details</legend>
      <AccountDetails {errors} {data} />
      <legend class="subtitle">Payment Types</legend>
      <PaymentTypes {errors} {data} />
      <legend class="subtitle">Options</legend>
      <PaymentOptions {errors} {data} />
    {/if}
  </form>
</div>

<Navigation {goToPrevious}>
  <Button type="submit" slot="next">
    Next

    {#if $pending}
      <Spinner transition={{ func: scale, params: { duration: 150 } }} />
    {/if}
  </Button>
</Navigation>

<style>
  .beneficiary-bank-details {
    display: grid;
    gap: 32px;
    grid-template-columns: 1fr 1fr;
  }

  .beneficiary-type {
    grid-column: 1 / 3;
  }

  .beneficiary-type > legend {
    font-size: 24px;
    margin: 8px 0;
  }

  .radio-container {
    align-items: center;
    display: flex;
  }

  .beneficiary-type > .radio-container {
    margin: 24px 0 0;
  }

  .subtitle {
    font-size: 24px;
    grid-column: 1 /3;
  }

  .beneficiary-type > p {
    color: grey;
    font-size: 16px;
    font-weight: 300;
    margin-top: 8px;
  }

  .radio-container > label {
    margin: 0 32px 0 8px;
  }
</style>
