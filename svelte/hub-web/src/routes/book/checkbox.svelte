<script lang="ts">
  import CheckIcon from "components/icons/check-icon.svelte";
  import { getRandomId } from "utils/random";

  export let id = getRandomId("checkbox");
  export let checked = false;
  export let label: string;
</script>

<label class="checkbox">
  <input type="checkbox" {id} bind:checked />

  <span class="box">
    {#if checked}
      <CheckIcon color="var(--color-common-dark-strong)" />
    {/if}
  </span>

  <span>{label}</span>
</label>

<style>
  .checkbox {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    cursor: pointer;
  }

  input {
    display: none;
  }

  .box {
    display: inline-block;
    min-width: 20px;
    min-height: 20px;
    vertical-align: middle;
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    cursor: pointer;
  }

  input:checked + span {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-main-primary-500);
    border: unset;
  }
</style>
