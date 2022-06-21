<script lang="ts">
  import Button from "$lib/components/ui/button.svelte";
  import SupportIcon from "$lib/icons/support-icon.svelte";
  import Header from "./_components/header.svelte";
  import HowItWorks from "./_components/how-it-works/how-it-works.svelte";
  import Login from "./_components/login.svelte";
</script>

<svelte:head>
  <title>Junction | Login</title>
</svelte:head>

<main>
  <HowItWorks />

  <section class="content">
    <Header />

    <Login />

    <Button><SupportIcon /> Support</Button>
  </section>
</main>

<style>
  main {
    display: grid;
    grid-template-columns: 482px 1fr;
    height: 100vh;
  }

  .content > :global(button) {
    background-color: var(--color-gray-lightest);
    border-radius: 44px;
    color: var(--color-black);
    height: 44px;
    justify-self: flex-end;
    margin: 30px;
    padding: 0 18px;
  }

  .content > :global(button > svg) {
    margin-right: 5px;
    vertical-align: middle;
  }

  .content {
    background-color: var(--color-white);
    display: grid;
    grid-template-rows: 137px 1fr 104px;
  }

  .content > :global(.login) {
    align-self: center;
    justify-self: center;
    max-width: 422px;
    width: 100%;
  }
</style>
