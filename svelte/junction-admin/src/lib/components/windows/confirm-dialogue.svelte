<script lang="ts" context="module">
  export type ConfirmDialogueProps = {
    title?: string;
    message: string;
    onConfirm?: () => void;
    onReject?: () => void;
    confirmLabel?: string;
    rejectLabel?: string;
  };
</script>

<script lang="ts">
  import { onMount } from "svelte";
  import Button from "../ui/button.svelte";
  import Window from "./window.svelte";

  export let title: string = undefined;
  export let message: string;
  export let onConfirm: () => void = undefined;
  export let onReject: () => void = undefined;
  export let confirmLabel = "OK";
  export let rejectLabel = "Cancel";
  export let close: () => void;
  export let focused: boolean;

  let container: HTMLDivElement;

  function confirm(): void {
    onConfirm?.();
    close();
  }

  function reject(): void {
    onReject?.();
    close();
  }

  onMount(() => {
    container.querySelector<HTMLButtonElement>(".confirm-dialogue button")?.focus();

    function keyPress(e: KeyboardEvent): void {
      if (!focused) {
        return;
      }

      if (e.code === "Escape") {
        reject();
      }
    }

    function input(e: KeyboardEvent): void {
      switch (e.code) {
        case "ArrowLeft":
        case "ArrowRight":
        case "ArrowUp":
        case "ArrowDown":
          container
            .querySelector<HTMLButtonElement>(".confirm-dialogue button:not(:focus)")
            ?.focus();
          break;
      }
    }

    window.addEventListener("keydown", keyPress);
    window.addEventListener("keydown", input);

    return () => {
      window.removeEventListener("keydown", keyPress);
      window.removeEventListener("keydown", input);
    };
  });
</script>

<Window {title} on:close={reject} {focused} bind:container maxWidth="400px">
  <div class="confirm-dialogue">
    <p>{message}</p>

    <div class="actions">
      <Button on:click={confirm}>{confirmLabel}</Button>
      <Button on:click={reject}>{rejectLabel}</Button>
    </div>
  </div>
</Window>

<style>
  .confirm-dialogue {
    font-size: 14px;
    user-select: none;
    padding: 8px 16px;
  }

  p {
    text-align: center;
    line-height: 1.3;
    margin-bottom: 24px;
  }

  .actions {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .actions > :global(button) {
    padding: 0 16px;
    height: 34px;
  }

  .actions > :global(:not(:first-child)) {
    margin-left: 8px;
    background-color: transparent;
    color: var(--color-teal);
  }
</style>
