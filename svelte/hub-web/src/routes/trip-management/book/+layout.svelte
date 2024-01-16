<script lang="ts" context="module">
  const pages: (keyof LocaleData["pages"]["tripManagement"]["pages"]["book"]["pages"])[] = [
    "search",
    "select",
    "payment",
    "confirmation",
  ];
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import StepView from "components/page/step-view.svelte";
  import { getLocaleData, type LocaleData } from "i18n";

  const i18n = getLocaleData();

  let steps: { label: string; number: number; title: string }[];

  $: i18nBook = $i18n.pages.tripManagement.pages.book;
  $: steps = pages.map((item, idx) => ({
    label: i18nBook.pages[item].title,
    number: idx + 1,
    title: i18nBook.pages[item].subTitle,
  }));
  $: activeStep = getActiveStep($page.route.id);
  $: title = steps.find((step) => step.number === activeStep)?.title;

  function getActiveStep(route: string | null): number {
    if (route?.endsWith("select-offer")) {
      return 2;
    } else if (route?.endsWith("payment")) {
      return 3;
    } else if (route?.endsWith("confirmation")) {
      return 4;
    }

    return 1;
  }
</script>

<div class="header">
  <h1 typography="headline-medium" weight="bold">{title}</h1>
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
    padding: 16px 24px;
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
