<script lang="ts">
  import clickOutside from "$lib/actions/click-outside";
  import { slide } from "svelte/transition";
  import TextField from "./text-field.svelte";

  type TValue = $$Generic<{ toString: () => string }>;

  export let value: TValue | undefined = undefined;
  export let items: TValue[] = [];

  let expanded = false;
  let partiallyExpanded = false;

  $: customHead = $$slots.head;
  $: customBody = $$slots.body;

  function toggle(): void {
    expanded = !expanded;
  }

  function collapse(): void {
    expanded = false;
  }

  function select(item: TValue): void {
    value = item;
    collapse();
  }
</script>

<div class="select-field" use:clickOutside={collapse} aria-expanded={partiallyExpanded}>
  <div class="wrapper">
    <div class="head" on:click={toggle}>
      {#if customHead}
        <slot name="head" {value} />
      {:else}
        <TextField value={value?.toString() ?? ""} readOnly placeholder="Choose Currencies" />
      {/if}
    </div>

    {#if expanded}
      <div
        class="body"
        transition:slide={{ duration: 150 }}
        on:introstart={() => (partiallyExpanded = true)}
        on:outroend={() => (partiallyExpanded = false)}
      >
        {#if customBody}
          <slot name="body" {select} {value} />
        {:else}
          <ul class="options">
            {#each items as item}
              <li class="option" aria-selected={item === value} on:click={() => select(item)}>
                {item.toString()}
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .select-field {
    border-radius: 10px;
    display: inline-block;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-size: 14px;
    height: 44px;
    outline: 0;
  }

  .wrapper {
    background-color: var(--color-white);
    border: var(--color-gray-lightest) 1px solid;
    border-radius: inherit;
    display: inline-block;
    font-size: 14px;
    left: 0;
    min-height: 100%;
    position: relative;
    top: 0;
    transition: border-color var(--speed-fast) ease, box-shadow var(--speed-fast) ease;
    width: 100%;
  }

  .select-field[aria-expanded="true"] > .wrapper {
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
    box-shadow: 0 4px 12px rgb(0 0 0 / 12%);
    z-index: 1;
  }

  .head {
    cursor: pointer;
    height: 100%;
    position: relative;
  }

  .head::after {
    border: 0 solid var(--color-gray-lighter);
    border-width: 2px 2px 0 0;
    content: "";
    display: block;
    height: 8px;
    position: absolute;
    right: 0;
    top: 50%;
    transform: translate(-180%, -80%) rotateZ(135deg);
    transition: transform var(--speed-fast) ease;
    width: 8px;
  }

  .select-field[aria-expanded="true"] > .wrapper > .head::after {
    transform: translate(-180%, -20%) rotateZ(315deg);
  }

  .head > :global(.text-field) {
    background-color: transparent;
    border: transparent;
    cursor: pointer;
    font-family: inherit;
    font-size: 16px;
    padding-left: 21px;
    padding-right: 21px;
    vertical-align: top;
  }

  .body {
    border-top: 1px solid var(--color-gray-lightest);
    max-height: 300px;
    overflow-y: auto;
  }

  .option {
    cursor: pointer;
    font-size: 16px;
    margin: 12px 0;
    padding: 7px 21px;
  }

  .options:not(:hover) > .option[aria-selected="true"],
  .option:hover {
    background-color: var(--color-light-background);
  }
</style>
