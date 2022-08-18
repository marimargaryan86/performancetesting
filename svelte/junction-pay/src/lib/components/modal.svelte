<script lang="ts">
  import type { ModalOptions } from "$models/modal-models";
  import { onMount } from "svelte";
  import { fade, scale } from "svelte/transition";
  import { close, modal } from "../stores";

  export let options: ModalOptions = {};
  export let title = "";
  export let type: string;

  let scrollEnabled = true;
  let modalEl: HTMLElement;
  const titleId = `${title}-modal-heading`;

  function handleTabKey(e: KeyboardEvent) {
    const focusableElements = modalEl.querySelectorAll<HTMLElement>(
      'a[href], input:not(:disabled), button:not(:disabled), area, textarea:not(:disabled), [tabindex="0"]',
    );

    const first = focusableElements[0];
    const last = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Escape") {
      closeModal();
    }

    if (e.key === "Tab") {
      handleTabKey(e);
    }
  }

  function closeModal() {
    scrollEnabled = true;
    close();
    $modal.firstFocusElement?.focus();
  }

  $: if (scrollEnabled) {
    document.body.style.overflow = "";
  } else {
    document.body.style.overflow = "hidden";
  }

  onMount(() => {
    scrollEnabled = false;
    document.addEventListener("keydown", handleKeydown);

    return () => {
      scrollEnabled = true;
      document.removeEventListener("keydown", handleKeydown);
    };
  });
</script>

<div
  transition:fade
  tabindex="-1"
  role="dialog"
  class="modal-wrapper"
  on:click|self={() => close()}
>
  <div
    class={`modal modal-${type}`}
    role="document"
    aria-modal={true}
    aria-labelledby={titleId}
    bind:this={modalEl}
    transition:scale={{ delay: 50, duration: 300 }}
  >
    <div class="modal-head">
      <h3 class="title" id={titleId}>{title}</h3>
      <button type="button" on:click={closeModal}>
        <span aria-hidden={true}>&#10005;</span>
      </button>
    </div>
    <div class="modal-body">
      {options.message}
    </div>
    <div class="modal-actions">
      {#if options.showConfirmButton}
        <button
          class="modal-action-button confirm-button"
          on:click={() => options.confirmFunction?.()}
        >
          {options.confirmText || "Confirm"}
        </button>
      {/if}
      {#if options.showCancelButton}
        <button
          class="modal-action-button cancel-button"
          on:click={() => options.cancelFunction?.()}
        >
          {options.cancelText || "Cancel"}
        </button>
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-wrapper {
    background-color: rgb(25 25 25 / 77%);
    bottom: 0;
    height: 100%;
    left: 0;
    position: fixed;
    right: 0;
    top: 0;
    width: 100%;
  }

  .modal {
    background-color: var(--color-white);
    box-shadow: 4px 14px 20px rgb(0 0 0 / 25%);
    margin: 10% auto;
    max-height: 75vh;
    max-width: 800px;
    overflow-y: auto;
    padding: 0 0 40px 56px;
    padding: 40px;
    width: 55%;
  }

  .modal-head {
    align-items: center;
    display: flex;
    justify-content: space-between;
    margin-bottom: 26.4px;
  }

  .modal-body {
    color: black;
    margin: 24px 0 40px;
  }

  .modal-actions {
    display: flex;
    gap: 16px;
    justify-content: end;
  }

  .modal-action-button {
    background: var(--color-black);
    border-radius: 10px;
    color: var(--color-white);
    font-size: 16px;
    height: 45px;
    padding: 12px 24px;
  }

  .confirm-button {
    background: linear-gradient(68.24deg, #ff7d37 -3.47%, #ffa574 103.83%);
  }

  .cancel-button {
    font-size: 14px;
  }

  .title {
    font-size: 32px;
    margin: 0;
  }

  button {
    align-self: flex-start;
    appearance: none;
    background-color: transparent;
    border: 0;
    color: var(--color-gray);
    font-size: 24px;
  }

  button:hover {
    cursor: pointer;
  }

  button:focus {
    outline: 1px solid var(--color-gray-lighter);
  }

  .dialog {
    border-radius: 0;
  }

  .modal-warning {
    color: var(--color-orange);
  }

  .modal-error {
    color: var(--color-red);
  }
</style>
