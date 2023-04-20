<script lang="ts">
  import CopyIcon from "components/icons/copy-icon.svelte";

  let className: string | undefined = undefined;

  export { className as class };
  export let maxWidth: string | undefined = undefined;
  export let width: string | undefined = undefined;
  export let copyable = false;
  export let copyAlign: "left" | "right" = "left";

  let copyRef: HTMLButtonElement;
  let copied = false;

  function copy(): void {
    copied = true;
    navigator.clipboard.writeText(copyRef.textContent?.trim() ?? "");

    setTimeout(() => (copied = false), 1500);
  }
</script>

<td class={className} style:--max-width={maxWidth} style:--width={width}>
  <div>
    <slot />
  </div>

  {#if copyable}
    <button
      class="copy"
      class:right-aligned={copyAlign === "right"}
      bind:this={copyRef}
      on:click={copy}
    >
      {#if copied}
        Copied to clipboard
      {:else}
        <slot />

        <CopyIcon color="var(--color-common-dark-strong)" />
      {/if}
    </button>
  {/if}
</td>

<style>
  td {
    position: relative;
    width: var(--width);
    max-width: var(--max-width);
    padding: 16px;
    border-bottom: var(--color-main-neutral-50) 1px solid;
  }

  div {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .copy {
    position: absolute;
    top: 16px;
    left: 8px;
    z-index: 10;
    display: flex;
    gap: 4px;
    align-items: center;
    margin: 0;
    padding: 4px 8px;
    color: var(--color-common-dark-strong);
    font-weight: inherit;
    font-size: inherit;
    font-family: inherit;
    white-space: nowrap;
    background-color: var(--color-main-primary-600);
    border: 0;
    border-radius: 4px;
    cursor: pointer;
    opacity: 0;
    pointer-events: none;
  }

  .copy.right-aligned {
    right: 0;
    left: unset;
  }

  td:hover > .copy {
    opacity: 1;
    pointer-events: all;
  }
</style>
