<script lang="ts" context="module">
  function getTimeLeft(date: Date): string {
    const secondsTotal = Math.max(0, Math.round((date.getTime() - new Date().getTime()) / 1000));
    const minutes = Math.round(secondsTotal / 60);
    const seconds = secondsTotal % 60;

    return `${minutes < 10 ? "0" : ""}${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  }
</script>

<script lang="ts">
  import AlertIcon from "components/icons/alert-icon.svelte";
  import CloseIcon from "components/icons/close-icon.svelte";
  import { onDestroy, onMount } from "svelte";
  import { slideFade } from "transitions/slide-fade";
  import { sleep } from "utils/common";

  export let expiresAt: Date;
  export let show = false;

  $: timeLeft = getTimeLeft(expiresAt);
  let ticking = show;

  async function tick(): Promise<void> {
    if (!ticking) {
      return;
    }

    timeLeft = getTimeLeft(expiresAt);

    if (timeLeft === "00:00") {
      return;
    }

    await sleep(1000);

    return tick();
  }

  export function close(): void {
    show = false;
    ticking = false;
  }

  export function open(): void {
    show = true;
    ticking = true;
    tick();
  }

  onMount(tick);

  onDestroy(() => {
    ticking = false;
  });
</script>

{#if show}
  <div class="countdown" transition:slideFade={{ duration: 400 }}>
    <span class="content">
      <AlertIcon />

      <strong class="typography body-medium bold">Time remaining</strong>
      <span class="typography body-medium">
        {timeLeft} mins to <strong class="typography bold">complete</strong> your booking
      </span>
    </span>

    <button on:click={close}><CloseIcon variant="cross" /></button>
  </div>
{/if}

<style>
  .countdown {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    background-color: var(--color-semantic-warning-100);
    border: var(--color-semantic-warning-600) 1px solid;
    border-radius: 16px;
  }

  .content {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .content > :global(svg) {
    flex-shrink: 0;
  }

  button {
    justify-self: flex-end;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
