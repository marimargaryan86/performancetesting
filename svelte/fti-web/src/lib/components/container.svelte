<script>
  /**
   * Basic container that provides the common "card" styles seen across the app.
   * Use this to construct primitives or reusable UI components.
   *
   */
</script>

<div class="container">
  <slot />
</div>

<style>
  .container {
    background: var(--background-white);
    border-radius: 8px;
    height: auto;
    width: auto;
  }
</style>
