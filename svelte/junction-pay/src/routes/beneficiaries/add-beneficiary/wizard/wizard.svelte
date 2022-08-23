<script lang="ts">
  import Wizard from "$lib/components/wizard.svelte";
  import persistentStore from "$lib/persistent-store";
  import type {
    BeneficiaryData,
    CompanyDetailsData,
    IndividualDetailsData,
  } from "$models/beneficiary-models/models";
  import { validateBeneficiaryData } from "$models/beneficiary-models/validators";
  import instances from "$services/instances";
  import BankAccountDetails from "./bank-account-details/bank-account-details.svelte";
  import BeneficiaryDetails from "./beneficiary-details.svelte";
  import Complete from "./complete.svelte";
  import Review from "./review.svelte";

  let data = persistentStore.writableSession<Partial<BeneficiaryData>>(
    "beneficiary-data",
    () => ({
      type: "company",
      paymentTypes: ["regular"],
      paymentOptions: [],
    }),
    (data) => {
      const companyData = data as Partial<CompanyDetailsData>;

      companyData.companyRegistrationDate = companyData.companyRegistrationDate
        ? new Date(companyData.companyRegistrationDate)
        : undefined;

      const individualData = data as Partial<IndividualDetailsData>;

      individualData.individualBirthDate = individualData.individualBirthDate
        ? new Date(individualData.individualBirthDate)
        : undefined;

      return data;
    },
  );

  async function create(): Promise<void> {
    if (validateBeneficiaryData($data)) {
      throw new Error("Invalid data");
    }

    await instances.beneficiary.create($data as BeneficiaryData);
  }
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
    <BeneficiaryDetails {goToNext} bind:data={$data} />
  {:else if value === "bank-account-details"}
    <BankAccountDetails {goToNext} {goToPrevious} bind:data={$data} />
  {:else if value === "review"}
    <Review
      goToNext={async () => {
        try {
          await create();

          goToNext();
        } catch {
          //
        }
      }}
      {goToPrevious}
      data={$data}
    />
  {:else if value === "complete"}
    <Complete resetStore={data.reset} />
  {/if}
</Wizard>
