<script lang="ts">
  type TValue = $$Generic<string | number>;

  export let id: string | undefined = undefined;
  export let group: TValue | undefined = undefined;
  export let value: Readonly<TValue> | undefined = undefined;
</script>

<div class="radio">
  <input type="radio" bind:group {value} {id} />
  <span class="selected" />
</div>

<style>
  .radio {
    background-color: var(--color-white);
    border: var(--color-gray-light) 1px solid;
    border-radius: 50%;
    cursor: pointer;
    display: inline-block;
    height: 24px;
    width: 24px;
  }

  .radio:focus-within {
    border: var(--color-teal) 2px solid;
  }

  input {
    cursor: inherit;
    display: block;
    height: 100%;
    margin: 0;
    opacity: 0;
    width: 100%;
  }

  .selected {
    align-items: center;
    background-color: var(--color-green);
    border-radius: 50%;
    bottom: calc(100% + 1px);
    display: flex;
    float: left;
    height: calc(100% + 2px);
    justify-content: center;
    pointer-events: none;
    position: relative;
    right: 1px;
    transition: opacity var(--speed-fast) ease;
    width: calc(100% + 2px);
  }

  .selected::before {
    border: var(--color-white) 0 solid;
    border-width: 0 2px 2px 0;
    content: "";
    display: block;
    height: 12px;
    transform: translateY(-1px) rotateZ(45deg);
    width: 6px;
  }

  input:not(:checked) ~ .selected {
    opacity: 0;
  }
</style>
