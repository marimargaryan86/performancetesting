<script lang="ts" context="module">
  function getTimeLeft(date: Date): string {
    const secondsTotal = Math.max(0, getTimeDeltaS(date, new Date(), false));
    const minutes = Math.floor(secondsTotal / 60);
    const seconds = secondsTotal % 60;

    return `${minutes < 10 ? "0" : ""}${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  }
</script>

<script lang="ts">
  import Icon from "$lib/components/icons/icon.svelte";
  import Alert from "$lib/components/ui/alert.svelte";
  import { getTranslator } from "$lib/i18n";
  import { onDestroy } from "svelte";
  import { getTimeDeltaS } from "$lib/utils/date-time";
  import { browser } from "$app/environment";

  export let expiresAt: Date;
  export let show = false;
  export let type: "offer-search" | "price-quote";

  const t = getTranslator();

  let interval = 0;
  let timeLeft = getTimeLeft(expiresAt);

  $: if (browser) {
    if (show) {
      interval = setInterval(tick, 1000, []);
    } else {
      clearInterval(interval);
    }
  }

  function tick(): void {
    timeLeft = getTimeLeft(expiresAt);

    if (timeLeft === "00:00") {
      clearInterval(interval);
    }
  }

  export function close(): void {
    show = false;
  }

  export function open(): void {
    show = true;
  }

  onDestroy(() => {
    if (browser) {
      clearInterval(interval);
    }
  });
</script>

<Alert {show} type="warning" class="countdown">
  <Icon variant="alert-triangle" color="var(--color-semantic-warning-600)" />
  <strong typography="body-medium" weight="bold">{$t("sentences.timeRemaining")}</strong>
  <span typography="body-medium">
    <!-- eslint-disable svelte/no-at-html-tags -->
    {#if type === "offer-search"}
      {@html $t("sentences.offerSearchTimeRemainingInfo", { timeLeft })}
    {:else}
      {@html $t("sentences.priceQuoteTimeRemainingInfo", { timeLeft })}
    {/if}
  </span>
</Alert>
