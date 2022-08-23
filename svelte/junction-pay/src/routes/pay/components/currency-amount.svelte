<script lang="ts">
  import currenciesData from "$content/currencies";
  import SelectField from "$lib/components/select-field.svelte";
  import TextField from "$lib/components/text-field.svelte";
  import utils from "$lib/utils";
  import type { ValidationError } from "$models/common-models";
  import instances from "$services/instances";
  import { onMount } from "svelte";

  type Payment = { currency: string; amount: number; beneficiaryId: string };

  export let goToNext: () => void;
  export let data: Partial<Payment>;

  let errors: ValidationError<Payment> = {};

  const { beneficiary: service } = instances;
  const { func: fetchBeneficiarys } = utils.pendableCall(service.find.bind(service), false);

  const currencies = currenciesData.map((currency) => ({
    ...currency,
    toString: () => currency.code,
  }));

  async function submit(): Promise<void> {
    errors = {};
    try {
      goToNext();
    } catch (e) {
      errors = e as typeof errors;
    }
  }

  let beneficiaryNameList: string[] = [];

  async function fetchBeneficiaryListAndFormatName() {
    const beneficiary = await fetchBeneficiarys(2);

    beneficiaryNameList = beneficiary.beneficiaries.map(
      ({
        beneficiary_entity_type,
        beneficiary_company_name,
        beneficiary_first_name,
        beneficiary_last_name,
        id,
      }: {
        beneficiary_entity_type: string;
        beneficiary_company_name: string;
        beneficiary_first_name: string;
        beneficiary_last_name: string;
        id: string;
      }) => {
        const name =
          beneficiary_entity_type === "company"
            ? beneficiary_company_name
            : `${beneficiary_first_name} ${beneficiary_last_name}`;
        return {
          name,
          code: id,
          toString: () => name,
        };
      },
    );
  }

  onMount(async () => {
    fetchBeneficiaryListAndFormatName();
  });
</script>

<form class="beneficiary-details" on:submit|preventDefault={submit}>
  <h2 class="header">Currency</h2>
  <div class="field">
    <label for="currency" class:error={!!errors.currency && !data.currency}>Currency</label>
    <SelectField
      bind:value={data.currency}
      items={currencies.map((el) => el.toString())}
      placeholder="Select currency"
      id="currency"
      error={!!errors.currency && !data.currency}
    />
  </div>
  <div class="field">
    <label for="amount" class:error={!!errors.amount && !data.amount}>Amount</label>
    <TextField
      id="amount"
      bind:value={data.amount}
      placeholder="0.00"
      error={!!errors.amount && !data.amount}
    />
  </div>
  {#if data.amount && data.currency}
    <div class="field">
      <label for="currency" class:error={!!errors.beneficiaryId && !data.beneficiaryId}
        >Beneficiary</label
      >
      <SelectField
        bind:value={data.beneficiaryId}
        items={beneficiaryNameList}
        placeholder="Please select a beneficiary"
        id="currency"
        error={!!errors.beneficiaryId && !data.beneficiaryId}
      />
    </div>
  {/if}
</form>

<style>
  .beneficiary-details {
    display: grid;
    gap: 60px 36px;
    grid-template-columns: 1fr 1fr;
  }

  .header {
    font-size: 21.6px;
    grid-column: 1 / 3;
  }

  .field > label {
    display: block;
    font-size: 18px;
    margin-bottom: 12px;
    transition: color var(--speed-fast) ease;
    width: max-content;
  }

  .field > label.error {
    color: var(--color-red);
  }

  .beneficiary-details > :global(button) {
    background-color: var(--color-orange);
    font-size: 20px;
    height: 56px;
    justify-self: flex-end;
    width: 310px;
  }

  .field > :global(.text-field) {
    padding: 0 18px;
  }

  .beneficiary-details > :global(button > .spinner) {
    margin-left: 8px;
    vertical-align: middle;
  }

  .field > :global(.text-field.text-field),
  .field > :global(.select-field.select-field) {
    border-color: transparent;
    box-shadow: 0 4px 30px rgb(0 0 0 / 8%);
    font-size: 18px;
    height: 61px;
    width: 100%;
  }
</style>
