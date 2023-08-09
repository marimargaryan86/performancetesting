<script lang="ts">
  import { clickOutside } from "directives/click-outside";
  import Dialogue from "./dialogue.svelte";

  export let fareRule: string;

  let expanded = false;

  function open(): void {
    expanded = true;
  }

  function close(): void {
    expanded = false;
  }

  function toggle(): void {
    if (expanded) {
      close();
    } else {
      open();
    }
  }

  function handleKeyToggle(event: KeyboardEvent): void {
    if (event.key === "Enter") {
      toggle();
    }
  }
</script>

<div use:clickOutside={close}>
  <button on:click={toggle} on:keyup={handleKeyToggle} class="fare-rule">
    <span class="typography typography body-small">View fare rule</span>
  </button>

  {#if expanded}
    <Dialogue {fareRule} />
  {/if}
</div>

<style>
  .fare-rule {
    display: block;
    margin-top: 4px;
    padding: 0;
    color: var(--color-common-light-text-link);
    text-align: right;
    text-decoration: underline;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
