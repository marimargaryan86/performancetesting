<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";

  type TSteps = $$Generic<Record<string, string>>;
  type TValue = Readonly<keyof TSteps>;

  export let steps: TSteps;
  export let value: TValue | undefined;
  export let urlNavigation = false;
  export let queryParamKey = "step";

  $: ids = Object.keys(steps);
  $: idCount = ids.length;
  $: activeIndex = ids.indexOf(value as string);
  $: queryParamStep = urlNavigation ? $page.url.searchParams.get(queryParamKey) : undefined;

  $: if (queryParamStep) {
    const id = queryParamStep;

    if (ids.indexOf(id) === -1) {
      value = ids[0];
    } else {
      value = id;
    }
  } else {
    value = ids[0];
  }

  function navigate(): void {
    if (urlNavigation) {
      const nextUrl = new URL($page.url);

      if (value === ids[0]) {
        nextUrl.searchParams.delete(queryParamKey);
      } else {
        nextUrl.searchParams.set(queryParamKey, value as string);
      }

      goto(nextUrl.toString());
    }
  }

  function goToNext(): void {
    value = ids[Math.min(idCount - 1, activeIndex + 1)];

    navigate();
  }

  function goToPrevious(): void {
    value = ids[Math.max(0, activeIndex - 1)];

    navigate();
  }
</script>

<div class="wizard">
  <div class="steps">
    {#each ids as id, idx}
      <span class="step" class:active={id === value} class:completed={activeIndex > idx}>
        <span>{idx + 1}</span>
        <strong>{steps[id]}</strong>
      </span>
    {/each}
  </div>

  <slot {value} steps={Object.keys(steps)} {goToNext} {goToPrevious} />
</div>

<style>
  .steps {
    display: flex;
    margin-bottom: 60px;
  }

  .step {
    align-items: center;
    color: var(--color-orange);
    display: flex;
    flex: 1 1 0;
    flex-flow: column;
    gap: 12px;
    justify-content: flex-start;
    position: relative;
    transition: color var(--speed-fast) ease;
  }

  .step::after,
  .step::before {
    border-bottom: var(--color-orange) 2px solid;
    content: "";
    display: block;
    position: absolute;
    top: 16px;
    transition: border-color var(--speed-fast) ease;
    width: calc(50% - 17px);
  }

  .step::after {
    right: 0;
  }

  .step::before {
    left: 0;
  }

  .step:first-child::before,
  .step:last-child::after {
    display: none;
  }

  .step > span {
    align-items: center;
    background-color: var(--color-white);
    border: var(--color-orange) 2px solid;
    border-radius: 50%;
    display: flex;
    height: 34px;
    justify-content: center;
    transition: background-color var(--speed-fast) ease, border-color var(--speed-fast) ease;
    width: 34px;
  }

  .step.completed > span {
    background-color: var(--color-orange);
    color: var(--color-white);
  }

  .step.active {
    color: var(--color-orange);
    font-weight: 500;
  }

  .step.active > span {
    border-color: var(--color-orange);
  }

  .step > strong {
    text-align: center;
  }

  .step.active ~ .step {
    color: var(--color-orange-light);
  }

  .step.active ~ .step > span {
    border: var(--color-orange-light) 2px solid;
  }

  .step.active::after,
  .step.active ~ .step::after,
  .step.active ~ .step::before {
    border-color: var(--color-orange-light);
  }
</style>
