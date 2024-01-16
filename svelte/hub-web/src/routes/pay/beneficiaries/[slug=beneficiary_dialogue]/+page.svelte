<script lang="ts" context="module">
  export type Step = "beneficiary" | "account" | "summary";

  function getSteps(
    mode: "edit" | "create",
  ): Record<
    Step,
    { prev?: Step; next?: Step; buttonLabel: string; number: number; label: string }
  > {
    return {
      beneficiary: {
        prev: undefined,
        next: "account",
        buttonLabel: "Next",
        number: 1,
        label: "Beneficiary Details",
      },
      account: {
        prev: "beneficiary",
        next: "summary",
        buttonLabel: "Verify",
        number: 2,
        label: "Bank Account Details",
      },
      summary: {
        prev: "account",
        next: undefined,
        buttonLabel: `${mode === "edit" ? "Update" : "Create"} Beneficiary`,
        number: 3,
        label: "Summary",
      },
    };
  }
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { writableCookie } from "utils/persistent-store";
  import StepView from "components/page/step-view.svelte";
  import routeConfig from "routeConfig";
  import BeneficiaryDetails from "./beneficiary-details.svelte";
  import BankAccountDetails from "./bank-account-details.svelte";
  import Summary from "./summary.svelte";
  import { URLExtended } from "utils/url";
  import StandardLayout from "components/page/standard-layout.svelte";
  import Alert from "components/ui/alert.svelte";
  import type { BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
  import { getPageTitle } from "utils/page-title";

  export let data;

  let stepComponent: BeneficiaryDetails | BankAccountDetails | Summary | undefined;
  let error: string | undefined = undefined;

  const beneficiary = writableCookie<BeneficiaryPut>({
    key: "beneficiary-data",
    value: data.beneficiary,
  });

  $: steps = getSteps(data.beneficiary.id ? "edit" : "create");
  $: step = ($page.url.searchParams.get("step") ?? "beneficiary") as Step;
  $: title = `${data.beneficiary.id ? "Edit" : "Add"} Beneficiary`;
  $: breadCrumbs = [
    { label: "Beneficiaries", url: routeConfig.routes.pay.routes.beneficiaries.root },
    {
      label: title,
      url: routeConfig.routes.pay.routes.beneficiaries.routes.beneficiary(data.beneficiary.id).root,
    },
  ];

  async function goToPrevious(): Promise<void> {
    await goto(new URLExtended($page.url, { query: { step: steps[step].prev } }));
  }

  async function goToNext(): Promise<void> {
    if ((await stepComponent?.validate()) ?? true) {
      await goto(new URLExtended($page.url, { query: { step: steps[step].next } }));
    }
  }

  async function cancel(): Promise<void> {
    if (!confirm("Are you sure you want to cancel?")) {
      return;
    }

    beneficiary.remove();

    await goto(routeConfig.routes.pay.routes.beneficiaries.root);
  }
</script>

<svelte:head>
  <title>{getPageTitle("Junction Hub", "Pay", "Beneficiaries", title)}</title>
</svelte:head>

<StandardLayout {breadCrumbs} pageTitle={title}>
  <StepView steps={Object.values(steps)} activeStep={steps[step].number} slot="steps" />

  <Alert class="error-message" type="error" show={Boolean(error)}>
    <span typography="body-medium">
      <strong weight="bold">Error</strong> <span>{error}</span>
    </span>
  </Alert>

  <div class="wrapper">
    {#if step === "beneficiary"}
      <BeneficiaryDetails
        accounts={data.accounts}
        bind:this={stepComponent}
        bind:data={$beneficiary}
      />
    {:else if step === "account"}
      <BankAccountDetails bind:this={stepComponent} bind:data={$beneficiary} />
    {:else if step === "summary"}
      <Summary bind:this={stepComponent} bind:data={$beneficiary} bind:error />
    {/if}
  </div>

  <button
    variant="text"
    size="medium"
    disabled={step === "beneficiary"}
    on:click={goToPrevious}
    slot="navigation-left"
  >
    Previous
  </button>

  <svelte:fragment slot="navigation-right">
    <button variant="outline" size="medium" on:click={cancel}>Cancel</button>
    <button variant="primary" size="medium" on:click={goToNext}>
      {steps[step].buttonLabel}
    </button>
  </svelte:fragment>
</StandardLayout>

<style>
  :global(.alert.error-message) {
    margin-bottom: 24px;
  }

  :global(.alert.error-message) strong {
    font-weight: 600;
  }

  .wrapper {
    display: flex;
    flex-flow: column;
    gap: 40px;
    height: 100%;
    padding: 56px 16px;
    overflow: auto;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
