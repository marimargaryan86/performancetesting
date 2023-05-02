<script lang="ts">
  import type { PageData } from "./$types";

  export let data: PageData;

  $: ({ beneficiary } = data);
</script>

<svelte:head>
  <title>
    {beneficiary ? `Edit ${beneficiary.name}` : "Add beneficiary"} · Beneficiaries · Pay · Junction Hub
  </title>
</svelte:head>

<div>
  <h1>{data.beneficiary ? "Editing" : "Create new"}</h1>
  <h2>{JSON.stringify(data.beneficiary)}</h2>
</div>
