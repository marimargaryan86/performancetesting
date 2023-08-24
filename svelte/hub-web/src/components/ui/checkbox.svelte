<script lang="ts" generics="TValue">
  /* global TValue */
  export let value: TValue | undefined = undefined;
  export let group: TValue[] = [];
  export let id: string | undefined = undefined;

  export let checked = value !== undefined && group.includes(value);

  $: updateCheckedByGroup(group);
  $: updateCheckedByChecked(checked);

  function updateCheckedByChecked(nextChecked: boolean): void {
    if (nextChecked && value !== undefined) {
      group = Array.from(new Set([...group, value]));
    } else if (value !== undefined) {
      group = group.filter((item) => item !== value);
    }
  }

  function updateCheckedByGroup(nextGroup: TValue[]): void {
    checked = value !== undefined && nextGroup.includes(value);
  }
</script>

<input {id} type="checkbox" {value} bind:checked />

<style>
  input {
    margin: 0;
    cursor: pointer;
  }
</style>
