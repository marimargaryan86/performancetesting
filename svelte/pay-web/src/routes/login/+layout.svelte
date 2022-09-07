<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import SupportIcon from "$lib/icons/support-icon.svelte";
  import { setContext } from "svelte";
  import { writable } from "svelte/store";
  import Header from "./components/header.svelte";
  import HowItWorks from "./components/how-it-works/how-it-works.svelte";

  setContext("email", writable(""));
</script>

<main>
  <HowItWorks />

  <section class="content">
    <Header />

    <div class="wrapper">
      <slot />
    </div>

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
    grid-row: 3;
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
    overflow-x: hidden;
  }

  .wrapper {
    align-self: center;
    justify-self: center;
    max-width: 422px;
    width: 100%;
  }
</style>
