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
    font-weight: 400;
    color: var(--color-white);
  }

  .sub-menu > :global(a) {
    color: inherit;
    text-decoration: none;
    font-weight: inherit;
    font-size: 12px;
    margin: 0 8px;
  }
</style>
