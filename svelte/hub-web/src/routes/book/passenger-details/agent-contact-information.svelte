<script lang="ts">
  import TextField from "components/ui/text-field.svelte";
  import SelectField from "components/ui/select-field.svelte";
  export let agentContactInformation: Partial<{
    name: string;
    countryCode: string;
    phoneNumber: string;
    email: string;
    addressFirst: string;
    addressSecond: string;
    city: string;
    country: string;
    postCode: string;
  }> = {};

  const countries = ["Spain", "Portugal", "France", "Andorra", "Gibraltar", "Morocco"];
</script>

<div class="agent-contact-form">
  <h3 class="agent-title">Agent's contact information</h3>
  <TextField
    class="agency-name"
    type="text"
    bind:value={agentContactInformation.name}
    placeholder="Agency name"
    label="Agency name"
    required
  />
  <div class="phone-number">
    <SelectField
      class="country-code"
      options={["+34", "+351", "+33", "+376", "+350", "+212", "+1"]}
      bind:value={agentContactInformation.countryCode}
      placeholder="Code"
      label="Country code"
      required
    />
    <TextField
      class="phone-number"
      type="text"
      bind:value={agentContactInformation.phoneNumber}
      placeholder="Phone number"
      label="Phone number"
      required
    />
  </div>
  <TextField
    class="email"
    type="email"
    bind:value={agentContactInformation.email}
    placeholder="Email"
    label="Email"
    required
  />
  <TextField
    class="address"
    type="text"
    bind:value={agentContactInformation.addressFirst}
    placeholder="Address line 1"
    label="Address line 1"
    required
  />
  <TextField
    class="address"
    type="text"
    bind:value={agentContactInformation.addressSecond}
    placeholder="Oficina 13"
    label="Address line 2"
  />
  <div class="location">
    <TextField
      class="city"
      type="text"
      bind:value={agentContactInformation.city}
      placeholder="Málaga"
      label="Town / City"
      required
    />
    <SelectField
      label="Country"
      required
      placeholder="Select"
      options={countries}
      bind:value={agentContactInformation.country}
    />
    <TextField
      class="post-code"
      type="text"
      bind:value={agentContactInformation.postCode}
      placeholder="Postcode"
      label="Postcode"
      required
    />
  </div>
</div>

<style>
  h3 {
    font-weight: 600;
    font-size: 22px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .agent-contact-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
    width: 100%;
    margin-bottom: 50px;
    padding: 40px 80px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
  }

  .agent-title {
    padding-bottom: 16px;
  }

  .phone-number {
    display: flex;
    flex-direction: row;
    gap: 24px;
    width: 100%;
  }

  .location {
    display: flex;
    flex-direction: row;
    gap: 24px;
    width: 100%;
  }

  .agent-contact-form :global(.text-field .wrapper) {
    width: 100%;
    height: 40px;
  }

  .agent-contact-form :global(.select-field .wrapper) {
    width: 100%;
    height: 40px;
  }

  .agent-contact-form :global(.text-field) {
    width: 100%;
  }

  .agent-contact-form :global(.select-field) {
    width: 100%;
  }

  .agent-contact-form :global(.text-field.post-code) {
    max-width: 112px;
  }

  .agent-contact-form :global(.select-field.country-code) {
    max-width: 130px;
  }

  .agent-contact-form :global(.select-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }

  .agent-contact-form :global(.text-field label) {
    font-weight: 600;
    font-size: 16px;
    font-family: Inter, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 26px;
  }
</style>
