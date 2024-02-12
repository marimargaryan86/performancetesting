<script lang="ts" context="module">
  type YouTubeVideo = {
    title: string;
    description: string;
    id: string;
    lengthS: number;
  };
</script>

<script lang="ts">
  import { page } from "$app/stores";
  import Icon from "$lib/components/icons/icon.svelte";
  import Backdrop from "$lib/components/ui/backdrop.svelte";

  let backdrop: Backdrop | undefined;
  let video: YouTubeVideo | undefined;

  export function open(nextVideo: YouTubeVideo): void {
    video = nextVideo;

    backdrop?.open();
  }

  export function close(): void {
    video = undefined;

    backdrop?.close();
  }
</script>

<Backdrop bind:this={backdrop}>
  <button on:click={close}>
    <Icon variant="close-circled" color="var(--color-common-dark-strong)" size="50px" />
  </button>

  {#if video}
    <iframe
      src="https://www.youtube.com/embed/{video.id}?autoplay=1&origin={$page.url.origin}&rel=0"
      title={video.title}
      frameborder="0"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen
    ></iframe>
  {/if}
</Backdrop>

<style>
  button {
    position: absolute;
    top: 24px;
    right: 24px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }

  iframe {
    width: 100%;
    max-width: 1040px;
    margin: 16px;
    aspect-ratio: 1.77;
  }
</style>
