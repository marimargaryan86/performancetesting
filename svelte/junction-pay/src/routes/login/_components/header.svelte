<script lang="ts">
  import Button from "$lib/components/button.svelte";
  import JunctionLogo from "$lib/images/junction-logo.svelte";
</script>

<header>
  <JunctionLogo detailed />

  <section class="sign-up">
    <span>Don't have an account?</span>

    <Button>Sign Up</Button>
  </section>
</header>

<style>
  header {
    align-items: center;
    display: flex;
    justify-content: space-between;
    padding: 0 50px;
  }

  .sign-up {
    color: var(--color-gray);
    font-size: 16px;
  }

  .sign-up > :global(button) {
    margin-left: 13px;
  }
</style>
