<script lang="ts">
  import { invalidateAll } from "$app/navigation";

  async function signOut(): Promise<void> {
    document.cookie = "session-token=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/; secure=true;";
    await invalidateAll();
  }
</script>

<main>
  <button on:click={signOut} class="primary large typography title-medium bold">Sign out</button>
</main>

<style>
  main {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }
</style>
