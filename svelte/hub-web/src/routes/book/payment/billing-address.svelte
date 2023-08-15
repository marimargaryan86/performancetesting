<script lang="ts" context="module">
  export type BillingAddressModel = {
    addressLine1: string | undefined;
    addressLine2: string | undefined;
    townOrCity: string | undefined;
    country: string | undefined;
    postcode: string | undefined;
  };
</script>

<script lang="ts">
  import TextField from "components/ui/text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";

  export let billingAddress: BillingAddressModel;

  const countries = ["Spain", "Portugal", "France", "Andorra", "Gibraltar", "Morocco"];
</script>

<div class="billing-address-form">
  <h3>Billing address</h3>
  <TextField
    bind:value={billingAddress.addressLine1}
    label="Address line 1"
    placeholder="Required"
    required
  />
  <TextField bind:value={billingAddress.addressLine2} label="Address line 2" />
  <div class="location">
    <TextField
      bind:value={billingAddress.townOrCity}
      class="city"
      placeholder="Málaga"
      label="Town / City"
      required
    />
    <SelectField
      bind:value={billingAddress.country}
      label="Country"
      required
      placeholder="Select"
      options={countries}
    />
    <TextField
      bind:value={billingAddress.postcode}
      class="post-code"
      type="text"
      placeholder="Postcode"
      label="Postcode"
      required
    />
  </div>
</div>

<style>
  h3 {
    margin-bottom: 16px;
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .billing-address-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .location {
    display: flex;
    flex-direction: row;
    gap: 24px;
    width: 100%;
  }

  .billing-address-form :global(.text-field.post-code) {
    max-width: 112px;
  }
</style>
