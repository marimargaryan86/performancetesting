<script lang="ts">
  import CheckIcon from "components/icons/check-icon.svelte";

  export let currentStep: 1 | 2 | 3 = 1;
</script>

<div class="book-steps-wrapper">
  <div class="book-steps container">
    <div class="current-step">
      <span class="{currentStep === 1 ? 'active' : 'successful'} step-circle typography body-small">
        {#if currentStep === 1}
          1
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Search</span>
    </div>
    <div class="step-line {currentStep >= 1 ? 'active-line' : 'inactive-line'}" />
    <div class="current-step">
      <span
        class="{currentStep === 2 ? 'active' : ''} {currentStep < 2
          ? 'inactive'
          : 'successful'} step-circle typography body-small"
      >
        {#if currentStep <= 2}
          2
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Select</span>
    </div>
    <div class="step-line {currentStep === 3 ? 'active-line' : 'inactive-line'}" />
    <div class="current-step">
      <span class="{currentStep < 3 ? 'inactive' : 'active'} step-circle typography body-small"
        >3</span
      >
      <span class="step-text typography body-medium">Summary</span>
    </div>
  </div>
</div>

<style>
  .successful {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-100);
    border: 2px solid var(--color-main-primary-500);
  }

  .book-steps-wrapper {
    display: flex;
    align-items: center;
    height: 56px;
    padding-left: 24px;
    background-color: var(--color-main-primary-50);
  }

  .book-steps {
    display: flex;
    align-content: center;
    align-items: center;
    max-width: 384px;
  }

  .book-steps span {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .step-line {
    width: 52px;
    height: 1px;
    margin-right: 8px;
  }

  .active-line {
    border-top: 2px solid var(--color-main-primary-500);
  }

  .inactive-line {
    border-top: 2px solid var(--color-main-primary-200);
  }

  .current-step {
    display: flex;
    align-items: center;
    margin-right: 8px;
  }

  .step-text {
    margin-left: 8px;
  }

  .step-circle {
    width: 24px;
    height: 24px;
    border-radius: 50%;
  }

  .current-step .active {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
    border: 2px solid var(--color-main-primary-500);
  }

  .current-step .inactive {
    width: 24px;
    height: 24px;
    color: unset;
    background-color: unset;
    border: 2px solid var(--color-main-primary-200);
    border-radius: 50%;
  }
</style>
