<script lang="ts">
  import CheckIcon from "components/icons/check-icon.svelte";

  export let currentStep: 1 | 2 | 3 | 4 | 5 = 1;
</script>

<div class="book-steps-wrapper">
  <div class="book-steps container">
    <div class="current-step">
      <span
        class="step-circle typography body-small"
        class:active={currentStep === 1}
        class:successful={currentStep > 1}
      >
        {#if currentStep === 1}
          1
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Search</span>
    </div>
    <div class="step-line" class:active-line={currentStep > 1} />
    <div class="current-step">
      <span
        class="step-circle typography body-small"
        class:active={currentStep === 2}
        class:successful={currentStep > 2}
      >
        {#if currentStep <= 2}
          2
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Select</span>
    </div>
    <div class="step-line" class:active-line={currentStep > 2} />
    <div class="current-step">
      <span
        class="step-circle typography body-small"
        class:active={currentStep === 3}
        class:successful={currentStep > 3}
      >
        {#if currentStep <= 3}
          3
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Passenger Details</span>
    </div>
    <div class="step-line" class:active-line={currentStep > 3} />
    <div class="current-step">
      <span
        class="step-circle typography body-small"
        class:active={currentStep === 4}
        class:successful={currentStep > 4}
      >
        {#if currentStep <= 4}
          4
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Payment</span>
    </div>
    <div class="step-line" class:active-line={currentStep > 4} />
    <div class="current-step">
      <span
        class="step-circle typography body-small"
        class:active={currentStep === 5}
        class:successful={currentStep > 5}
      >
        {#if currentStep <= 5}
          5
        {:else}
          <CheckIcon color="var(--color-main-primary-500)" />
        {/if}
      </span>
      <span class="step-text typography body-medium">Confirmation</span>
    </div>
  </div>
</div>

<style>
  .step-circle.successful {
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
    max-width: 1100px;
    height: 56px;
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
    border-top: 2px solid var(--color-main-primary-200);
  }

  .active-line {
    border-top: 2px solid var(--color-main-primary-500);
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
    color: unset;
    background-color: unset;
    border: 2px solid var(--color-main-primary-200);
    border-radius: 50%;
  }

  .current-step .active {
    color: var(--color-common-dark-strong);
    background-color: var(--color-main-primary-500);
    border: 2px solid var(--color-main-primary-500);
  }
</style>
