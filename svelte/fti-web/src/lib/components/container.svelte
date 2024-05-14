<script lang="ts">
  export let title: string | undefined = undefined;
</script>

<!--
  * Basic container that provides the common "card" styles seen across the app.
  * Provides a configurable header, widget, and subtitle. Use this to construct
  * primitives or reusable UI components.
  * -->
<div class="container">
  {#if title}
    <header>
      <div class="title">
        <h2>{title}</h2>
        <slot name="header-widget" />
      </div>
      <div class="subtitle">
        <slot name="header-subtitle" />
      </div>
    </header>
  {/if}

  <slot name="content" />
</div>

<style>
  .container {
    display: flex;
    background: var(--background-white);
    border-radius: var(--border-radius, 8px);
    height: auto;
    width: auto;
  }

  header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    width: 100%;
    padding: 36px 24px;
  }

  .title {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .title h2 {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: var(--title-font-weight, 600);
    font-size: var(--title-font-size, 24px);
    line-height: var(--title-line-height, 30px);
  }
</style>
