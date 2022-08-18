<script lang="ts">
  import Checkbox from "$lib/components/checkbox.svelte";
  import type { AddBeneficiaryBankDetailsCombined } from "$models/beneficiary-models";
  import type { ValidationError } from "$models/common-models";
  import AccountInfoForm from "./account-info-form.svelte";
  import IbanAccountInfo from "./iban-account-info.svelte";

  export let data: Partial<AddBeneficiaryBankDetailsCombined>;
  export let errors: ValidationError<AddBeneficiaryBankDetailsCombined>;
</script>

<fieldset>
  <div class="swift">
    <Checkbox value="swift" bind:group={data.options} checked={false} />
    <label for="swift">Swift</label>
  </div>
  <div class="sort_code">
    <Checkbox value="sort_code" bind:group={data.options} checked={true} />
    <label for="sort_code">Sort code</label>
  </div>
</fieldset>
{#if data.options?.includes("sort_code")}
  <AccountInfoForm {errors} {data} />
{/if}
{#if data.options?.includes("swift")}
  <IbanAccountInfo {errors} {data} types={data.options} />
{/if}

<style>
  fieldset {
    align-items: center;
    display: flex;
    gap: 32px;
    grid-column: 1 / 3;
  }
</style>
