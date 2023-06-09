<script lang="ts" context="module">
  export type Step = "beneficiary" | "account" | "summary";

  const steps: Record<
    Step,
    { prev?: Step; next?: Step; buttonLabel: string; number: number; label: string }
  > = {
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
      buttonLabel: "Create Beneficiary",
      number: 3,
      label: "Summary",
    },
  };
</script>

<script lang="ts">
  import BreadCrumbs from "components/page/bread-crumbs.svelte";
  import type { PageData } from "./$types";
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

  export let data: PageData;

  const beneficiary = writableCookie<CreateBeneficiaryModel>({
    key: "beneficiary-data",
    value: data.beneficiary ?? {},
    overwrite: true,
  });

  $: step = ($page.url.searchParams.get("step") ?? "beneficiary") as Step;
  $: title = `${data.beneficiary ? "Edit" : "Add"} Beneficiary`;
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

    await goto(url);
  }

  async function cancel(): Promise<void> {
    if (!confirm("Are you sure you want to cancel?")) {
      return;
    }

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
  <div class="wrapper">
    {#if step === "beneficiary"}
      <BeneficiaryDetails bind:data={$beneficiary} countries={data.countries} />
    {:else if step === "account"}
      <BankAccountDetails
        bind:data={$beneficiary}
        countries={data.countries}
        currencies={data.currencies}
      />
    {:else if step === "summary"}
      <Summary data={$beneficiary} countries={data.countries} currencies={data.currencies} />
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

  .content {
    flex-grow: 1;
    padding: 24px;
    overflow: auto;
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
