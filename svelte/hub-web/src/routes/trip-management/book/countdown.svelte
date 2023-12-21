<script lang="ts" context="module">
  function getTimeLeft(date: Date): string {
    const secondsTotal = Math.max(0, getTimeDeltaS(date, new Date(), false));
    const minutes = Math.floor(secondsTotal / 60);
    const seconds = secondsTotal % 60;

    return `${minutes < 10 ? "0" : ""}${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  }
</script>

<script lang="ts">
  import AlertIcon from "components/icons/alert-icon.svelte";
  import Alert from "components/ui/alert.svelte";
  import { getLocaleData } from "i18n";
  import { onDestroy, onMount } from "svelte";
  import { sleep } from "utils/common";
  import { getTimeDeltaS } from "utils/date-time";

  export let expiresAt: Date;
  export let show = false;

  const i18n = getLocaleData();

  let ticking = show;

  $: timeLeft = getTimeLeft(expiresAt);

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

<Alert {show} type="warning" class="countdown">
  <AlertIcon />
  <strong class="typography body-medium bold">{$i18n.sentences.timeRemaining}</strong>
  <span class="typography body-medium">
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    {@html $i18n.sentences.timeRemainingInfo.replace("{timeLeft}", timeLeft)}
  </span>
</Alert>
