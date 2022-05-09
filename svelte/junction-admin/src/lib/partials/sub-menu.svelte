<nav class="sub-menu">
  <slot />
</nav>

<style>
  .sub-menu {
    display: flex;
    align-items: center;
    background-color: var(--color-gray-darkest);
    height: 32px;
    box-shadow: var(--drop-shadow);
    user-select: none;
  }

  .sub-menu > :global(a) {
    text-decoration: none;
    color: var(--color-white);
    font-weight: 600;
    font-size: 12px;
    margin: 0 8px;
  }
</style>
