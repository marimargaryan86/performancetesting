<script lang="ts">
  import sections from "$content/how-it-works";
  import utils from "$lib/utils";
  import { onMount } from "svelte";
  import Content from "./content.svelte";

  const fadeDuration = 800;
  const flyDuration = 600;

  let activeIndex = 0;
  let flipFlop = false;

  $: activeIndex, (flipFlop = !flipFlop);
  $: section = sections[activeIndex];

  onMount(() => {
    let running = true;

    async function transition(): Promise<void> {
      await utils.sleep(section.duration);

      activeIndex = (activeIndex + 1) % sections.length;

      if (running) {
        transition();
      }
    }

    transition();

    return () => (running = false);
  });
</script>

<section class="how-it-works">
  {#if flipFlop}
    <Content {section} {fadeDuration} {flyDuration} />
  {:else}
    <Content {section} {fadeDuration} {flyDuration} />
  {/if}
</section>

<style>
  .how-it-works {
    overflow: hidden;
    position: relative;
  }
</style>
