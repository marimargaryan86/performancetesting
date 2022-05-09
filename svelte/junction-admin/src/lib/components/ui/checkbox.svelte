<script lang="ts">
  type T = $$Generic<string | number>;

  export let title: string = undefined;
  export let label: string = undefined;
  export let value: T = undefined;
  export let group: T[] = undefined;
  export let checked = false;

  $: updateChecked(group);
  $: updateGroup(checked);

  function updateChecked(group?: T[]) {
    if (!group) {
      return;
    }

    checked = group?.indexOf(value) !== -1;
  }

  function updateGroup(checked: boolean) {
    if (!group) {
      return;
    }

    group = checked ? [...group, value] : group.filter((item) => item !== value);
  }
</script>

<label class="checkbox" {title}>
  <input type="checkbox" bind:checked {value} on:input on:change />

  <svg
    class="checked"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M22 0H2C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V22C0 22.5304 0.210714 23.0391 0.585786 23.4142C0.960859 23.7893 1.46957 24 2 24H22C22.5304 24 23.0391 23.7893 23.4142 23.4142C23.7893 23.0391 24 22.5304 24 22V2C24 1.46957 23.7893 0.960859 23.4142 0.585786C23.0391 0.210714 22.5304 0 22 0ZM2 22V2H22V22H2Z"
      fill="#47A08B"
    />
    <path d="M10 17.5L5 12.54L6.59 11L10 14.35L17.41 7L19 8.58L10 17.5Z" fill="#47A08B" />
  </svg>

  <svg
    class="unchecked"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M22 0H2C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V22C0 22.5304 0.210714 23.0391 0.585786 23.4142C0.960859 23.7893 1.46957 24 2 24H22C22.5304 24 23.0391 23.7893 23.4142 23.4142C23.7893 23.0391 24 22.5304 24 22V2C24 1.46957 23.7893 0.960859 23.4142 0.585786C23.0391 0.210714 22.5304 0 22 0ZM2 22V2H22V22H2Z"
      fill="#47A08B"
    />
    <path d="M2 2H22V22H2V2Z" />
  </svg>

  {#if label}<span>{label}</span>{/if}
</label>

<style>
  .checkbox {
    height: 20px;
    /* width: 20px; */
    display: inline-block;
    cursor: pointer;
    border-radius: 4px;
  }

  .checkbox:focus-within > svg {
    box-shadow: var(--focus-outline-dark);
  }

  input {
    pointer-events: none;
    position: absolute;
    opacity: 0;
    height: 0;
    width: 0;
    line-height: 0;
    padding: 0;
    margin: 0;
  }

  svg {
    height: 20px;
    width: 20px;
    vertical-align: middle;
    border-radius: 2px;
    background-color: var(--color-white);
  }

  .checked {
    background-color: var(--color-teal-lighter);
  }

  input:not(:checked) ~ .checked {
    display: none;
  }

  input:checked ~ .unchecked {
    display: none;
  }

  span {
    display: inline-block;
    vertical-align: middle;
    margin-left: 4px;
  }
</style>
