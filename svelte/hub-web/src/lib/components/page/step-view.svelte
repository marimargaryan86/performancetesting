<script lang="ts">
  import Icon from "$lib/components/icons/icon.svelte";

  export let steps: { label: string; number: number }[];
  export let activeStep: number;
</script>

<ul class="step-view">
  {#each steps as step}
    {@const done = activeStep > step.number}

    <li class:active={activeStep === step.number} class:done>
      <span typography="body-small" weight="bold" class="number-badge">
        {#if done}
          <Icon variant="checked" size="16px" color="var(--color-main-primary-500)" />
        {:else}
          {step.number}
        {/if}
      </span>
      <span typography="body-medium">{step.label}</span>
    </li>
  {/each}
</ul>

<style>
  .step-view {
    display: flex;
    gap: 8px;
    padding: 16px 24px;
    background-color: var(--color-main-primary-50);
  }

  li {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  li:not(:first-child)::before {
    display: block;
    width: 52px;
    height: 0;
    border-bottom: var(--color-main-primary-100) 1px solid;
    content: "";
  }

  span {
    color: var(--color-common-light-strong);
  }

  .number-badge {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border: var(--color-main-primary-200) 1px solid;
    border-radius: 50%;
    transition:
      background 150ms ease,
      border 150ms ease,
      color 150ms ease;
  }

  .active > .number-badge {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
    border-color: transparent;
  }

  .done > .number-badge {
    color: transparent;
    background-color: var(--color-main-primary-100);
    border-color: var(--color-main-primary-500);
  }
</style>
