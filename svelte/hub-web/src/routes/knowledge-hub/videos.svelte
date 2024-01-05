<script lang="ts" context="module">
  function getDuration(lengthS: number): string {
    const minutes = Math.floor(lengthS / 60);
    const seconds = lengthS % 60;

    return [minutes ? `${minutes}m` : undefined, seconds ? `${seconds}s` : undefined]
      .filter(ensureDefined)
      .join(" ");
  }
</script>

<script lang="ts">
  import { getLocaleData } from "i18n";
  import { ensureDefined } from "utils/array";
  import Card from "components/ui/card.svelte";
  import ClockIcon from "components/icons/clock-icon.svelte";
  import PlayIcon from "components/icons/play-icon.svelte";
  import VideoPlayer from "./video-player.svelte";

  const i18n = getLocaleData();

  let videoPlayer: VideoPlayer | undefined;
</script>

<VideoPlayer bind:this={videoPlayer} />

<section>
  <h2 class="typography headline-small bold">{$i18n.pages.knowledgeHub.videos.title}</h2>
  <p class="typography title-medium">
    {$i18n.pages.knowledgeHub.videos.description}
  </p>

  <div class="videos">
    {#each $i18n.pages.knowledgeHub.videos.items as video}
      {@const action = videoPlayer?.open.bind(videoPlayer.open, video)}
      <Card variant="vertical">
        <button
          slot="media"
          class="media-button"
          style:background-image="url(https://img.youtube.com/vi/{video.id}/mqdefault.jpg)"
          on:click={action}
        >
          <PlayIcon variant="circle" />
        </button>

        <svelte:fragment slot="content">
          <span class="chip typography body-medium">
            <ClockIcon variant="outlined" />
            {getDuration(video.lengthS)}
          </span>

          <div class="info">
            <h3 class="typography title-large bold">{video.title}</h3>
            <p class="typography body-large">
              {video.description}
            </p>
          </div>
        </svelte:fragment>
      </Card>
    {/each}
  </div>
</section>

<style>
  section {
    display: flex;
    flex-flow: column;
    gap: 16px;
    color: var(--color-common-light-strong);
  }

  section > p {
    color: var(--color-common-light-medium);
  }

  .videos {
    display: grid;
    grid-template-columns: repeat(auto-fit, 373px);
    gap: 16px;
  }

  .media-button {
    width: 100%;
    height: 190px;
    padding: 0;
    background-repeat: no-repeat;
    background-size: cover;
    border: 0;
    border-radius: 16px 16px 0 0;
    cursor: pointer;
  }

  .chip {
    display: flex;
    gap: 8px;
    align-items: center;
    align-self: flex-start;
    width: fit-content;
    height: 32px;
    margin: 0;
    padding: 0 16px;
    color: var(--color-common-light-strong);
    background-color: transparent;
    border: var(--color-main-primary-100) 1px solid;
    border-radius: 16px;
  }

  .info {
    display: flex;
    flex-flow: column;
    gap: 16px;
    padding: 24px 0;
  }

  .info > p {
    color: var(--color-common-light-medium);
  }
</style>
