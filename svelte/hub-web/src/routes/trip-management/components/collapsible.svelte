<script lang="ts">
  import ChevronIcon from "components/icons/chevron-icon.svelte";
  import { slideFade } from "transitions/slide-fade";

  export let expandedOnMount = false;
  export let transitionTimeMs = 300;
  export let title = "";

  let expanded = expandedOnMount;

  export function close(): void {
    expanded = false;
  }

  export function open(): void {
    expanded = true;
  }

  export function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }
</script>

<div class:collapsible={true}>
  <button class="toggle" on:click={toggle}>
    <slot name="title" {expanded} {transitionTimeMs}>
      <span class="typography title-medium bold">{title}</span>
    </slot>

    <ChevronIcon size="20px" direction={expanded ? "up" : "down"} />
  </button>

  {#if expanded}
    <div class="content" transition:slideFade={{ duration: transitionTimeMs }}>
      <slot {expanded} {transitionTimeMs} />
    </div>
  {/if}

  <slot name="content-after" {expanded} {transitionTimeMs} />
</div>

<style>
  .collapsible {
    display: flex;
    flex-flow: column;
    gap: 16px;
    padding: 24px 40px;
    color: var(--color-text-light-strong);
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .toggle {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    padding: 0;
    color: var(--color-main-primary-900);
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
