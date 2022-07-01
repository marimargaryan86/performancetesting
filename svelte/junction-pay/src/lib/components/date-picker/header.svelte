<script lang="ts">
  import Button from "../button.svelte";
  import MonthPicker from "./month-picker.svelte";
  import YearPicker from "./year-picker.svelte";

  export let focusedMonth: Date;

  function increase(): void {
    focusedMonth.setMonth(focusedMonth.getMonth() + 1);
    focusedMonth = new Date(focusedMonth);
  }

  function decrease(): void {
    focusedMonth.setMonth(focusedMonth.getMonth() - 1);
    focusedMonth = new Date(focusedMonth);
  }
</script>

<div class="header">
  <MonthPicker bind:date={focusedMonth} />
  <YearPicker bind:date={focusedMonth} />

  <div class="navigation">
    <Button on:click={decrease} />
    <Button on:click={increase} />
  </div>
</div>

<style>
  .header {
    align-items: center;
    display: grid;
    gap: 4px;
    grid-template-columns: max-content max-content 1fr;
  }

  .navigation {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  .header > :global(button),
  .navigation > :global(button) {
    background-color: transparent;
    color: var(--color-orange);
    font-size: 20px;
    height: unset;
    padding: 0;
  }

  .navigation > :global(button) {
    padding: 4px;
  }

  .navigation > :global(button::after) {
    border: 0 solid var(--color-orange);
    border-width: 2px 2px 0 0;
    content: "";
    display: block;
    height: 12px;
    transform: rotateZ(45deg);
    width: 12px;
  }

  .navigation > :global(button:first-child::after) {
    transform: rotateZ(-135deg);
  }
</style>
