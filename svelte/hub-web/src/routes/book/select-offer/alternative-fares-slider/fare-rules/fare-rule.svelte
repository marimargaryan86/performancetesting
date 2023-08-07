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
  <div on:click={toggle} on:keyup={handleKeyToggle} class="fare-rule">
    <span class="typography typography body-small ">View fare rule</span>
  </div>

  {#if expanded}
    <Dialogue {fareRule} />
  {/if}
</div>

<style>
  .fare-rule {
    display: block;
    margin-top: 4px;
    color: var(--color-common-light-text-link);
    text-align: right;
    text-decoration: underline;
    cursor: pointer;
  }
</style>
