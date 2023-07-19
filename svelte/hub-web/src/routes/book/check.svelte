<script lang="ts">
  import CheckIcon from "components/icons/check-icon.svelte";
  export let isChecked = false;
  export let label: string;

  function toggleCheckbox(): void {
    isChecked = !isChecked;
  }
</script>

<label class="cursor checkbox-container">
  <input type="checkbox" class="hidden" />
  <span class="checkbox {isChecked ? 'checked' : ''}" on:click={toggleCheckbox}>
    {#if isChecked} <CheckIcon color="var(--color-common-dark-strong)" /> {/if}
  </span>
  <span class="checkbox-label" on:click={toggleCheckbox}>{label}</span>
</label>

<style>
  .checkbox-container {
    display: flex;
    align-items: center;
  }

  .checkbox-label {
    margin-left: 12px;
  }

  .checkbox {
    display: inline-block;
    min-width: 20px;
    min-height: 20px;
    vertical-align: middle;
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    cursor: pointer;
  }

  .checked {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-main-primary-500);
    border: unset;
  }

  .hidden {
    display: none;
  }

  .cursor {
    cursor: pointer;
  }
</style>
