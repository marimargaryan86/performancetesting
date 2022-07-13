<script lang="ts">
  import Wizard from "$lib/components/wizard.svelte";
  import BankAccountDetails from "./bank-account-details.svelte";
  import BeneficiaryDetails from "./beneficiary-details.svelte";
  import Complete from "./complete.svelte";
  import Review from "./review.svelte";
</script>

<Wizard
  steps={{
    "beneficiary-details": "Beneficiary details",
    "bank-account-details": "Bank account details",
    review: "Review",
    complete: "Complete",
  }}
  value="beneficiary-details"
  let:value
  let:goToNext
  let:goToPrevious
  urlNavigation
>
  {#if value === "beneficiary-details"}
    <BeneficiaryDetails {goToNext} />
  {:else if value === "bank-account-details"}
    <BankAccountDetails {goToNext} {goToPrevious} />
  {:else if value === "review"}
    <Review {goToNext} {goToPrevious} />
  {:else if value === "complete"}
    <Complete {goToPrevious} />
  {/if}
</Wizard>
