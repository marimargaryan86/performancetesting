<table>
  <slot />
</table>

<style>
  table {
    border-collapse: separate;
    text-align: left;
  }

  table :global(th) {
    background-color: rgb(255 255 255 / 20%);
    border: #ffffff 1px solid;
    border-width: 1px 0;
    font-weight: 500;
    padding: 14px 20px;
    vertical-align: middle;
  }

  table :global(td) {
    background-color: var(--color-white);
    color: var(--color-gray-darker);
    padding: 20px;
    vertical-align: middle;
  }

  table > :global(thead > tr) {
    border-radius: 10px;
    box-shadow: 0 -11px 37px rgb(0 0 0 / 3%);
    height: 45px;
  }

  table :global(tbody::before) {
    content: "";
    display: block;
    height: 18px;
  }

  table :global(tbody > tr) {
    position: relative;
  }

  table :global(th:first-child) {
    border-left-width: 1px;
    border-radius: 10px 0 0 10px;
  }

  table :global(th:last-child) {
    border-radius: 0 10px 10px 0;
    border-right-width: 1px;
  }

  table > :global(tbody > tr:not(:last-child)::after) {
    border: var(--color-gray-lightest) 1px solid;
    bottom: 0;
    content: "";
    left: 14px;
    opacity: 0.3;
    position: absolute;
    width: calc(100% - 28px);
  }

  table :global(tr:first-child > td:not(.empty):last-child) {
    border-radius: 0 10px 0 0;
  }

  table :global(tr:first-child > td:not(.empty):first-child) {
    border-radius: 10px 0 0;
  }

  table :global(tr:last-child > td:not(.empty):first-child) {
    border-radius: 0 0 0 10px;
  }

  table :global(tr:last-child > td:not(.empty):last-child) {
    border-radius: 0 0 10px;
  }
</style>
