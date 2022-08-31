<script lang="ts">
  import CheckedIcon from "$lib/icons/checked-icon.svelte";
  import routeConfig from "$lib/route-config";
  import { onMount } from "svelte";

  export let resetStore: () => void;

  onMount(async function () {
    resetStore();
  });
</script>

<div class="complete">
  <CheckedIcon />

  <div>
    <h2>Complete</h2>
    <p>Beneficiary created successfully</p>
    <a href={routeConfig.beneficiaries.root}>Back to beneficiaries</a>
  </div>
</div>

<style>
  .complete {
    align-items: center;
    background-color: var(--color-white);
    border-radius: 10px;
    display: grid;
    gap: 24px;
    grid-template-columns: max-content 1fr;
    padding: 24px;
  }

  h2 {
    font-size: 24px;
    margin-bottom: 12px;
  }

  p {
    color: var(--color-gray-light);
    font-size: 18px;
    margin-bottom: 24px;
  }

  a {
    color: var(--color-orange);
    text-decoration: none;
  }
</style>
