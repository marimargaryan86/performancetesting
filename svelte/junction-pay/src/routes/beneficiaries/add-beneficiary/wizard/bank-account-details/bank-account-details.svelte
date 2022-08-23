<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import Radio from "$lib/components/radio.svelte";
  import type {
    BankAccountDetailsData,
    BankAccountDetailsError,
  } from "$models/beneficiary-models/models";
  import { validateBankAccountDetails } from "$models/beneficiary-models/validators";
  import Navigation from "../navigation.svelte";
  import AccountDetails from "./account-details.svelte";
  import EntityDetails from "./entity-details.svelte";
  import PaymentOptions from "./payment-options.svelte";
  import PaymentTypes from "./payment-types.svelte";

  export let goToNext: () => void;
  export let goToPrevious: () => void;
  export let data: Partial<BankAccountDetailsData>;

  let errors: BankAccountDetailsError | undefined = undefined;

  async function submit(): Promise<void> {
    errors = validateBankAccountDetails(data);

    if (!errors) {
      goToNext();
    }
  }
</script>

<form class="bank-account-details" on:submit|preventDefault={submit}>
  <fieldset class="beneficiary-type">
    <legend>Beneficiary type</legend>

    <ul class="account-type">
      <li>
        <Radio value="company" bind:group={data.type} id="company" />
        <label for="company">Company</label>
      </li>

      <li>
        <Radio value="individual" bind:group={data.type} id="individual" />
        <label for="individual">Individual</label>
      </li>
    </ul>
  </fieldset>

  <EntityDetails {errors} bind:data />

  <legend>Account details</legend>
  <AccountDetails {errors} bind:data />

  <legend>Payment types</legend>
  <PaymentTypes {errors} bind:data />

  <legend>Options</legend>
  <PaymentOptions {errors} bind:data />

  <Navigation {goToPrevious}>
    <Button type="submit" slot="next">Next</Button>
  </Navigation>
</form>

<style>
  .bank-account-details {
    display: grid;
    gap: 36px;
    grid-template-columns: 1fr 1fr;
  }

  .beneficiary-type {
    grid-column: 1 / -1;
  }

  legend,
  .beneficiary-type > legend {
    font-size: 24px;
    grid-column: 1 / -1;
    margin: 8px 0 0;
  }

  .beneficiary-type > legend {
    margin: 8px 0 32px;
  }

  .account-type {
    margin: 0 0 0 8px;
  }

  .account-type > li {
    display: inline-block;
    margin: 0 32px 0 -8px;
  }

  .bank-account-details > :global(.navigation) {
    grid-column: 1 / -1;
  }

  .account-type > li > :global(.radio) {
    margin-right: 8px;
    vertical-align: middle;
  }
</style>
