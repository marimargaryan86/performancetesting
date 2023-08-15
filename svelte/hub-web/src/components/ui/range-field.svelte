<script lang="ts">
  import { browser } from "$app/environment";
  import { onDestroy, onMount } from "svelte";

  export let min: number;
  export let max: number;
  export let value: number | { start: number; end: number };

  let track: HTMLDivElement | undefined;
  let startHandle: HTMLDivElement | undefined;
  let endHandle: HTMLDivElement | undefined;
  let selectedHandle: HTMLDivElement | undefined;
  let dragStartPos: number | undefined = undefined;
  let initialValue: number | undefined = undefined;

  $: delta = Math.abs(max - min);
  $: startValue = typeof value === "number" ? value : value.start;
  $: endValue = typeof value === "number" ? undefined : value.end;
  $: start = ((startValue - min) / delta) * 100;
  $: end = endValue === undefined ? undefined : ((endValue - min) / delta) * 100;

  function beginMove(event: MouseEvent): void {
    selectedHandle = event.target as HTMLDivElement;
    dragStartPos = event.clientX;

    if (typeof value === "number") {
      initialValue = value;
    } else if (selectedHandle === startHandle) {
      initialValue = value.start;
    } else {
      initialValue = value.end;
    }
  }

  function endMove(): void {
    selectedHandle = undefined;
    dragStartPos = undefined;
    initialValue = undefined;
  }

  function move(event: MouseEvent): void {
    if (track && selectedHandle && dragStartPos !== undefined) {
      const trackWidth = track.getBoundingClientRect().width;
      const ratio = delta / trackWidth;
      const nextDelta = (initialValue ?? 0) + (event.clientX - dragStartPos) * ratio;

      updateValue(nextDelta);
    }
  }

  function updateValue(nextDelta: number): void {
    if (typeof value === "number") {
      value = Math.round(Math.max(Math.min(nextDelta, max), min));

      return;
    }

    if (selectedHandle === startHandle) {
      value.start = Math.round(Math.max(Math.min(nextDelta, value.end), min));
    } else if (selectedHandle === endHandle) {
      value.end = Math.round(Math.max(Math.min(nextDelta, max), value.start));
    }
  }

  onMount(() => {
    if (browser) {
      window.addEventListener("blur", endMove);
      window.addEventListener("mouseup", endMove);
      window.addEventListener("mousemove", move);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener("blur", endMove);
      window.removeEventListener("mouseup", endMove);
      window.removeEventListener("mousemove", move);
    }
  });
</script>

<div class="range-field">
  <div class="track" bind:this={track} class:span={typeof value !== "number"}>
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div
      class="start"
      style:--pos-x="calc({start}% - 8px)"
      bind:this={startHandle}
      on:dragstart|preventDefault={beginMove}
      draggable="true"
    />

    {#if end !== undefined}
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div
        class="end"
        style:--pos-x="calc({end}% + 8px)"
        bind:this={endHandle}
        on:dragstart|preventDefault={beginMove}
        draggable="true"
      />
    {/if}
  </div>
</div>

<style>
  .range-field {
    display: inline-flex;
    align-items: center;
    height: 16px;
  }

  .track {
    position: relative;
    width: 100%;
    height: 4px;
    margin: 0 0 0 16px;
  }

  .track.span {
    margin: 0 16px;
  }

  .track::after {
    display: block;
    height: 100%;
    margin: 0 0 0 -16px;
    background-color: #d2ede6;
    border-radius: 4px;
    content: "";
  }

  .track.span::after {
    margin: 0 -16px;
  }

  .start,
  .end {
    position: absolute;
    top: -150%;
    left: calc(var(--pos-x) - 8px);
    width: 16px;
    height: 16px;
    background-color: var(--color-main-primary-500);
    border-radius: 50%;
    cursor: pointer;
  }
</style>
