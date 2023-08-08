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
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import Button from "components/ui/button.svelte";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { writableCookie } from "utils/persistent-store";
  import type { CreateBeneficiaryModel } from "models/beneficiary";
  import StepView from "components/page/step-view.svelte";
  import routeConfig from "routeConfig";
  import BeneficiaryDetails from "./beneficiary-details.svelte";
  import BankAccountDetails from "./bank-account-details.svelte";
  import Summary from "./summary.svelte";
  import { slide } from "svelte/transition";

  export let data;

  let stepComponent: BeneficiaryDetails | BankAccountDetails | Summary | undefined;
  let error: string | undefined = undefined;

  const beneficiary = writableCookie<CreateBeneficiaryModel>({
    key: "beneficiary-data",
    value: data.beneficiary,
  });

  $: steps = getSteps(data.beneficiary.id ? "edit" : "create");
  $: step = ($page.url.searchParams.get("step") ?? "beneficiary") as Step;
  $: title = `${data.beneficiary.id ? "Edit" : "Add"} Beneficiary`;
  $: breadCrumbs = [
    { label: "Beneficiaries", url: routeConfig.pay.beneficiaries.root },
    { label: title, url: routeConfig.pay.beneficiaries.beneficiary(data.beneficiary.id) },
  ];

  async function goToPrevious(): Promise<void> {
    const url = new URL($page.url);
    const { prev } = steps[step];

    if (prev) {
      url.searchParams.set("step", prev);
    }

    await goto(url);
  }

  async function goToNext(): Promise<void> {
    const url = new URL($page.url);
    const { next } = steps[step];

    if (next) {
      url.searchParams.set("step", next);
    }

    if ((await stepComponent?.validate()) ?? true) {
      await goto(url);
    }
  }

  async function cancel(): Promise<void> {
    if (!confirm("Are you sure you want to cancel?")) {
      return;
    }

    beneficiary.remove();

    await goto(routeConfig.pay.beneficiaries.root);
  }
</script>

<svelte:head>
  <title>
    {title} · Beneficiaries · Pay · Junction Hub
  </title>
</svelte:head>

<BreadCrumbs items={breadCrumbs} />

<h1 class="typography headline-medium bold">{title}</h1>

<StepView steps={Object.values(steps)} activeStep={steps[step].number} />

<div class="content">
  {#if error}
    <div class="error typography body-medium" transition:slide|local={{ duration: 150 }}>
      <strong>Error</strong> <span>{error}</span>
    </div>
  {/if}

  <div class="wrapper">
    {#if step === "beneficiary"}
      <BeneficiaryDetails
        countries={data.countries}
        accounts={data.accounts}
        bind:this={stepComponent}
        bind:data={$beneficiary}
      />
    {:else if step === "account"}
      <BankAccountDetails
        countries={data.countries}
        currencies={data.currencies}
        bind:this={stepComponent}
        bind:data={$beneficiary}
      />
    {:else if step === "summary"}
      <Summary
        countries={data.countries}
        currencies={data.currencies}
        bind:this={stepComponent}
        bind:data={$beneficiary}
        bind:error
      />
    {/if}
  </div>
</div>

<div class="navigation">
  <Button variant="text" size="medium" disabled={step === "beneficiary"} on:click={goToPrevious}>
    Previous
  </Button>
  <span />
  <Button variant="outline" size="medium" on:click={cancel}>Cancel</Button>
  <Button variant="primary" size="medium" on:click={goToNext}>
    {steps[step].buttonLabel}
  </Button>
</div>

<style>
  .headline-medium {
    padding: 8px 24px 24px;
  }

  .error {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    padding: 18px;
    color: var(--color-common-light-strong);
    background-color: var(--color-semantic-error-100);
    border: var(--color-semantic-error-600) 1px solid;
    border-radius: 8px;
  }

  .error > strong {
    font-weight: 600;
  }

  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    padding: 24px;
    overflow: hidden;
    background-image: var(--color-gradient-extensions-horizontal);
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

  .navigation {
    display: flex;
    gap: 16px;
    padding: 16px 24px;
  }

  .navigation > span {
    flex-grow: 1;
  }

  .navigation > :global(:last-child) {
    min-width: 140px;
  }
</style>
