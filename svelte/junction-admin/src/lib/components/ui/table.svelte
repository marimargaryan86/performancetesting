<script lang="ts">
  import type { TransitionConfig } from "svelte/transition";

  type TransitionParams = $$Generic<unknown>;

  type Transition<U, T = (node: Element, params: U) => TransitionConfig> = {
    func: T;
    params: U;
  };

  export let stickyHeader = false;
  let _transition: Transition<TransitionParams> | undefined = undefined;
  export { _transition as transition };

  function transition(node: Element): TransitionConfig {
    return _transition?.func(node, _transition.params) ?? { duration: 0 };
  }
</script>

<table class="table" on:outroend transition:transition|local>
  <thead style:--position={stickyHeader ? "sticky" : "relative"}>
    <slot name="head" />
  </thead>

  <tbody>
    <slot name="body" />
  </tbody>
</table>

<style>
  .table {
    font-size: 12px;
    user-select: none;
  }

  .table > thead {
    position: var(--position);
    top: 0;
    left: 0;
    z-index: 1;
    color: var(--color-teal-dark);
    user-select: none;
  }

  .table > thead::after {
    position: absolute;
    top: 100%;
    left: 0;
    content: "";
    display: block;
    height: 8px;
    width: 100%;
    background-image: linear-gradient(0deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1));
    pointer-events: none;
  }

  .table :global(td) {
    vertical-align: middle;
    padding: 0 8px;
  }

  .table > thead :global(td) {
    position: relative;
    padding: 8px;
  }

  .table > thead :global(td > .sorter) {
    position: absolute;
    top: 6px;
    right: 8px;
  }

  .table :global(td.select) {
    width: 34px;
    padding: 0 8px;
  }

  .table :global(td.select > .checkbox) {
    vertical-align: top;
  }

  .table :global(td.actions) {
    text-align: right;
    padding: 0 8px;
    width: min-content;
    vertical-align: middle;
  }

  .table :global(tr) {
    background-color: var(--color-white);
    height: 30px;
  }

  .table > tbody > :global(tr) {
    cursor: var(--pointer-style);
    height: 34px;
  }

  .table > tbody > :global(tr:nth-child(odd)) {
    background-color: var(--color-gray-light);
  }

  .table > tbody > :global(tr:hover) {
    background-color: var(--color-teal-lighter);
    box-shadow: 0 0 1px 1px var(--color-teal-light) inset;
  }

  .table > tbody > :global(tr:not(:hover) > td.actions > *) {
    visibility: hidden;
  }
</style>
