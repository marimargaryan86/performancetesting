<script lang="ts">
  import Button from "components/ui/button.svelte";
  import { createEventDispatcher } from "svelte";

  const dispatch = createEventDispatcher<{ close: void }>();

  export let paymentProcessing = false;
  export let stripeErrorMessage: string | undefined = undefined;
  export let paymentSucceed = false;

  function close(): void {
    dispatch("close");
  }
</script>

{#if paymentProcessing || stripeErrorMessage || paymentSucceed}
  <div class="background">
    <div class="modal">
      {#if paymentSucceed}
        <img src="/images/payment-modal/success.png" alt="status" />
        <p class="typography body-medium">Success!</p>
        <h1 class="typography headline-medium bold">Payment successful</h1>
      {:else if stripeErrorMessage}
        <img src="/images/payment-modal/declined.png" width="96" alt="status" />
        <h1 class="typography headline-medium bold">Payment declined</h1>
        <p class="typography body-medium">{stripeErrorMessage}</p>
        <Button on:click={close}>Try again</Button>
      {:else if paymentProcessing}
        <div class="loader" />
        <p class="typography body-medium">In progress</p>
        <h1 class="typography headline-medium bold">Payment processing</h1>
      {/if}
    </div>
  </div>
{/if}

<style>
  .background {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    background-color: var(--color-alpha-channel-black-50);
  }

  .modal {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 482px;
    padding: 64px 0 48px;
    background-color: var(--color-common-dark-strong);
    border-radius: 16px;
    animation: fade-in 0.3s ease-in-out;
  }

  @keyframes fade-in {
    from {
      opacity: 0;
    }

    to {
      opacity: 1;
    }
  }

  img {
    padding-bottom: 32px;
  }

  h1 {
    padding-bottom: 8px;
  }

  .modal :global(button) {
    height: 48px;
    margin-top: 48px;
  }

  p {
    padding-bottom: 8px;
    color: var(--color-main-neutral-700);
  }

  .loader {
    width: 40px;
    height: 40px;
    margin-bottom: 32px;
    border: 4px solid var(--color-main-primary-50);
    border-top: 4px solid var(--color-main-primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }

    100% {
      transform: rotate(360deg);
    }
  }
</style>
