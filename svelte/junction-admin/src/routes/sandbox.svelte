<script lang="ts">
  import { checkboxGroup } from "$lib/checkbox-group";
  import { onMount } from "svelte";
  import { writable } from "svelte/store";

  let values = ["a", "b", "c", "d", "e", "f"];

  const valuesStore = writable(values);

  $: $valuesStore = values;
  const { toggleAll, group, allChecked, multiSelect, unsubscriber } = checkboxGroup(valuesStore);

  onMount(() => unsubscriber);
</script>

<div>
  <input type="checkbox" on:input={toggleAll} checked={$allChecked} /> All
  <ul>
    {#each values as value, idx}
      <li>
        <input type="checkbox" {value} bind:group={$group} on:input={() => multiSelect(idx)} />
        {value}
      </li>
    {/each}
  </ul>
  <button on:click={() => (values = [...values, "g", "h", "i"])}>Click me</button>
</div>
