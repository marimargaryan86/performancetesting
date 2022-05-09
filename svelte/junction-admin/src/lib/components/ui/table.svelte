<script lang="ts">
  /* TODO: Impl sorting. */
  import EditButton from "$lib/components/buttons/edit-button.svelte";
  import { onMount } from "svelte";
  import { flip } from "svelte/animate";
  import { fade } from "svelte/transition";
  import DeleteButton from "../buttons/delete-button.svelte";
  import Checkbox from "./checkbox.svelte";
  import Sorter from "./sorter.svelte";

  type T = $$Generic<{ id: string }>;

  export let selectable = false;
  export let actions: Partial<{
    edit: (value: T) => void;
    delete: (value: T) => void;
  }> = {};
  export let selectedIds: string[] = [];
  export let headers: { title: string; sortable?: boolean }[];
  export let values: T[];
  export let pageLimit = 1;
  export let formatter: (value: T) => (string | number)[];
  export let transitionTimeMs = 0;
  export let selectRowOnClick = false;

  let lastSelectedIndex: number = undefined;
  let shiftDown = false;

  $: if (values === undefined) {
    lastSelectedIndex = undefined;
  }
  $: allSelected = values.reduce((prev, curr) => prev && selectedIds.indexOf(curr.id) !== -1, true);
  $: hasActions = !!Object.keys(actions).length;

  function selectAll(e: InputEvent): void {
    selectedIds = (e.currentTarget as HTMLInputElement).checked
      ? values.map((value) => value.id)
      : [];
  }

  function toggleSelected(value: T): void {
    if (!selectable) {
      return;
    }

    if (selectedIds.indexOf(value.id) === -1) {
      selectedIds = [...selectedIds, value.id];
    } else {
      selectedIds = selectedIds.filter((nextId) => nextId !== value.id);
    }
  }

  function multiSelect(index: number): void {
    if (isNaN(lastSelectedIndex)) {
      lastSelectedIndex = index;
    }

    if (!shiftDown) {
      lastSelectedIndex = index;

      return;
    }

    const mode = selectedIds.indexOf(values[index].id) === -1 ? "select" : "deselect";
    const start = Math.min(index, lastSelectedIndex);
    const end = Math.max(index, lastSelectedIndex) + 1;
    const nextSelectedIds = values.slice(start, end).map((value) => value.id);

    if (mode === "select") {
      selectedIds = Array.from(new Set([...selectedIds, ...nextSelectedIds]));
    } else {
      selectedIds = selectedIds.filter((placeId) => nextSelectedIds.indexOf(placeId) === -1);
    }
  }

  onMount(() => {
    function toggle(e: KeyboardEvent) {
      shiftDown = e.shiftKey || false;
    }

    window.addEventListener("focus", toggle);
    window.addEventListener("keydown", toggle);
    window.addEventListener("keyup", toggle);

    return () => {
      window.removeEventListener("focus", toggle);
      window.removeEventListener("keydown", toggle);
      window.removeEventListener("keyup", toggle);
    };
  });
</script>

<table class="table" transition:fade|local={{ duration: transitionTimeMs }} on:outroend>
  <thead>
    <tr>
      {#if selectable}
        <td class="select">
          <Checkbox
            checked={allSelected}
            on:input={selectAll}
            title={`${allSelected ? "Deselect" : "Select"} all`}
          />
        </td>
      {/if}

      {#each headers as header, idx}
        <td>
          <span>{header.title}</span>

          {#if header.sortable}
            <Sorter />
          {/if}
        </td>
      {/each}

      {#if hasActions}
        <td />
      {/if}
    </tr>
  </thead>

  <tbody>
    {#each values.map((value) => ({ columns: formatter(value), value })) as row, idx (row.value.id)}
      <tr
        style="--pointer-style: {selectRowOnClick ? 'pointer' : 'default'}"
        on:click={selectRowOnClick ? () => toggleSelected(row.value) : undefined}
        in:fade={{ duration: 150, delay: (idx % pageLimit) * 15 }}
        animate:flip={{ duration: 250 }}
      >
        {#if selectable}
          <td class="select">
            <Checkbox
              value={row.value.id}
              bind:group={selectedIds}
              on:input={() => multiSelect(idx)}
            />
          </td>
        {/if}

        {#each row.columns as column}
          <td>{column}</td>
        {/each}

        {#if hasActions}
          <td class="actions">
            {#if actions.edit}
              <EditButton
                tabindex={-1}
                on:click={(e) => {
                  e.stopPropagation();
                  actions.edit(row.value);
                }}
                title="Edit"
              />
            {/if}

            {#if actions.delete}
              <DeleteButton
                tabindex={-1}
                on:click={(e) => {
                  e.stopPropagation();
                  actions.delete(row.value);
                }}
                title="Delete"
              />
            {/if}
          </td>
        {/if}
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .table {
    font-size: 12px;
    user-select: none;
  }

  thead {
    position: sticky;
    top: 0;
    left: 0;
    z-index: 1;
    color: var(--color-teal-dark);
    user-select: none;
  }

  thead::after {
    position: absolute;
    content: "";
    display: block;
    height: 8px;
    width: 100%;
    background-image: linear-gradient(0deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.1));
    pointer-events: none;
  }

  td {
    vertical-align: middle;
    padding: 0 8px;
  }

  thead td {
    position: relative;
    padding: 8px;
  }

  thead td > :global(.sorter) {
    position: absolute;
    top: 6px;
    right: 8px;
  }

  td.select {
    width: 34px;
    padding: 0 8px;
  }

  td.select > :global(.checkbox) {
    vertical-align: top;
  }

  td.actions {
    text-align: right;
    padding: 0 8px;
    width: min-content;
    vertical-align: middle;
  }

  tr {
    background-color: var(--color-white);
    height: 30px;
  }

  tbody > tr {
    cursor: var(--pointer-style);
    height: 34px;
  }

  tbody > tr:nth-child(odd) {
    background-color: var(--color-gray-light);
  }

  tbody > tr:hover {
    background-color: var(--color-teal-lighter);
    box-shadow: 0 0 1px 1px var(--color-teal-light) inset;
  }

  tbody > tr:not(:hover) > td.actions > :global(*) {
    visibility: hidden;
  }
</style>
