<script lang="ts">
  import { getRandomId } from "utils/random";

  export let id = getRandomId("checkbox");
  export let active = false;
</script>

<div class="switch">
  <input type="checkbox" {id} bind:checked={active} />
  <label for={id} />
</div>

<style>
  .switch {
    --x-height: var(--height, 24px);
    --x-width: var(--width, 40px);

    display: inline-block;
    width: var(--x-width);
    height: var(--x-height);
  }

  input {
    display: none;
  }

  label {
    display: inline-block;
    width: 100%;
    height: 100%;
    padding: 2px;
    text-align: left;
    vertical-align: top;
    background-color: var(--color-main-neutral-300);
    border-radius: var(--x-height);
    cursor: pointer;
  }

  input:checked + label {
    background-color: var(--color-main-primary-500);
  }

  label::before {
    --x-dimension: calc(var(--x-height) - 4px);

    display: inline-block;
    width: var(--x-dimension);
    height: var(--x-dimension);
    vertical-align: top;
    background-color: var(--color-common-background-light-main);
    border-radius: 50%;
    transition: margin-left 150ms ease;
    content: "";
  }

  input:checked + label::before {
    margin-left: calc(var(--x-width) - var(--x-dimension) - 4px);
  }
</style>
