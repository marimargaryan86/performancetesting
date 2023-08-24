<script lang="ts" context="module">
  const steps: { label: string; number: number; title: string }[] = [
    { label: "Search", number: 1, title: "Search for offers" },
    { label: "Select", number: 2, title: "Select an offer" },
    { label: "Payment", number: 3, title: "Payment" },
    { label: "Passenger Details", number: 4, title: "Passenger Details" },
    { label: "Confirmation", number: 5, title: "Confirmation" },
  ];
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import StepView from "components/page/step-view.svelte";

  $: activeStep = getActiveStep($page.route.id);
  $: title = steps.find((step) => step.number === activeStep)?.title;

  function getActiveStep(route: string | null): number {
    if (route?.endsWith("select-offer")) {
      return 2;
    } else if (route?.endsWith("passenger-details")) {
      return 4;
    } else if (route?.endsWith("payment")) {
      return 3;
    }

    return 1;
  }
</script>

<div class="header">
  <h1 class="typography headline-medium bold">{title ?? ""}</h1>
</div>

<StepView {steps} {activeStep} />

<div class="content">
  <slot />
</div>

<style>
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32px 24px;
    color: var(--color-main-neutral-800);
  }

  .content {
    display: flex;
    flex-flow: column;
    flex-grow: 1;
    overflow: auto;
    background-image: var(--color-gradient-extensions-horizontal);
  }
</style>
