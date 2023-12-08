<script lang="ts">
  import StandardLayout from "components/page/standard-layout.svelte";
  import Videos from "./videos.svelte";
  import Faq from "./faq.svelte";
</script>

<svelte:head>
  <title>Knowledge Hub · Junction Hub</title>
</svelte:head>

<StandardLayout pageTitle="Knowledge Hub" backgroundImage="none">
  <div class="content">
    <Videos />

    <Faq />
  </div>
</StandardLayout>

<style>
  .content {
    width: 100%;
    max-width: 1156px;
  }
</style>
