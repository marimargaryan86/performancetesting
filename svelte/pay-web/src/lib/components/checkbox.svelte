<script lang="ts">
  type TValue = $$Generic<string | number>;

  export let group: TValue[] | undefined = undefined;
  export let value: Readonly<TValue> | undefined = undefined;
  export let checked = false;
  export let id: string | undefined = undefined;

  $: updateChecked(group);
  $: updateGroup(checked);

  function updateChecked(group?: TValue[]) {
    if (group === undefined || value === undefined) {
      return;
    }

    checked = group.indexOf(value) !== -1;
  }

  function updateGroup(checked: boolean) {
    if (group === undefined || value === undefined) {
      return;
    }

    const set = new Set(group);

    if (checked) {
      set.add(value);
      group = Array.from(set);
    } else {
      set.delete(value);
      group = Array.from(set);
    }
  }
</script>

<input class="checkbox" type="checkbox" bind:checked {value} {id} />

<style>
  .checkbox {
    appearance: none;
    background-color: var(--color-white);
    border: var(--color-gray-light) 1px solid;
    border-radius: 4px;
    cursor: pointer;
    display: inline-block;
    height: 24px;
    margin: 0;
    outline: none;
    width: 24px;
  }

  .checkbox:focus-within {
    border: var(--color-teal) 2px solid;
  }

  .checkbox:checked {
    background-color: var(--color-green);
    border: 0;
  }

  .checkbox:checked::before {
    border: var(--color-white) 0 solid;
    border-width: 0 2px 2px 0;
    content: "";
    display: block;
    height: 12px;
    left: 9.6px;
    position: relative;
    top: 4.8px;
    transform: translateY(-1px) rotateZ(45deg);
    width: 6px;
  }
</style>
