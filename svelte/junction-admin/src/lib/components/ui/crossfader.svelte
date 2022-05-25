<script lang="ts">
  import { fade } from "svelte/transition";

  export let active: "first" | "second" = "first";
  export let transitionTimeMs = 300;

  let inTransition: "first" | "second" = "first";
</script>

{#if active === "first" && inTransition === "first"}
  <div
    class="crossfader"
    transition:fade|local={{ duration: transitionTimeMs }}
    on:outroend={() => (inTransition = "second")}
  >
    <slot name="first" />
  </div>
{:else if active === "second" && inTransition === "second"}
  <div
    class="crossfader"
    transition:fade|local={{ duration: transitionTimeMs }}
    on:outroend={() => (inTransition = "first")}
  >
    <slot name="second" />
  </div>
{/if}
