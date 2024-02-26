<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let active: boolean = false;
  export let theme: "light" | "dark" = "light";

  const dispatch = createEventDispatcher<{ select: void }>();

  function select(): void {
    dispatch("select");
  }
</script>

<button
  type="button"
  on:click={select}
  class="role-option"
  class:active
  class:dark={theme === "dark"}
  aria-pressed={active}
>
  {#if $$slots.media}
    <div class="media-wrapper">
      <slot name="media" />
    </div>
  {/if}

  {#if $$slots.content}
    <div class="content-wrapper">
      <slot name="content" />
    </div>
  {/if}
</button>

<style>
  button.role-option {
    --background-color: var(--color-common-background-light-main);

    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: space-between;
    width: 258px;
    height: 110px;
    padding: 16px;
    color: inherit;
    font-size: 1rem;
    font-family: inherit;
    text-align: left;
    background-color: var(--background-color);
    border: 1px solid var(--color-common-line-medium);
    border-radius: 8px;
    outline: none;
    cursor: pointer;
    transition:
      background-color 0.3s,
      border-color 0.3s,
      color 0.3s;
  }

  button.role-option.dark {
    --background-color: var(--color-main-primary-50);

    background-color: var(--background-color);
  }

  button.role-option.active {
    background-color: var(--color-main-primary-50);
    border: 2px solid var(--color-main-primary-500);
  }

  .media-wrapper {
    display: flex;
    justify-content: center;
  }

  .content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
    justify-content: space-between;
    overflow: hidden;
  }

  .content-wrapper > * {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
</style>
