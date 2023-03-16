<script lang="ts">
  type TValue = $$Generic;

  export let value: TValue | undefined = undefined;
  export let group: TValue[] = [];
  export let id: string | undefined = undefined;

  let checked = value && group.includes(value);

  $: {
    if (checked && value) {
      group = Array.from(new Set([...group, value]));
    } else if (value) {
      group = group.filter((item) => item !== value);
    }
  }
</script>

<input {id} type="checkbox" {value} bind:checked />

<style>
  input {
    margin: 0;
    cursor: pointer;
  }
</style>
