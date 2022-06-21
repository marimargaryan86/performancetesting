<script lang="ts">
  export let checked = false;
  export let id: string | undefined = undefined;
</script>

<label class="switch">
  <input type="checkbox" bind:checked {id} />
  <span />
</label>

<style>
  .switch {
    cursor: pointer;
    display: inline-block;
    height: 20px;
    width: 33px;
  }

  input {
    appearance: none;
    display: block;
    height: 0;
    margin: 0;
    outline: 0;
    padding: 0;
    width: 0;
  }

  span {
    background-color: var(--color-gray-lightest);
    border-radius: 20px / 20px;
    display: block;
    height: 100%;
    position: relative;
    transition: background-color 150ms ease;
    width: 100%;
  }

  input:checked + span {
    background-color: var(--color-teal);
  }

  span::before {
    background-color: var(--color-white);
    border-radius: 50%;
    box-shadow: 0 3px 8px rgb(0 0 0 / 15%), 0 3px 1px rgb(0 0 0 / 6%);
    content: "";
    display: block;
    height: 18px;
    left: 19px;
    position: absolute;
    top: 1px;
    transform: translateX(-100%);
    transition: left 150ms ease, right 150ms ease;
    width: 18px;
  }

  input:checked + span::before {
    left: calc(100% - 1px);
  }
</style>
