<script lang="ts" context="module">
  const videos: YouTubeVideo[] = [
    {
      title: "Search for a trip",
      description: "Find out how to search for rail trips in Junction Hub.",
      id: "qMTv6kNAIEU",
      lengthS: 60,
    },
    {
      title: "Select an offer",
      description: "Find out how to select an offer for your customer’s booking in Junction Hub.",
      id: "JdfyhZU3kQg",
      lengthS: 69,
    },
    {
      title: "Add passenger details",
      description: "Find out how to add passenger details to a rail booking in Junction Hub.",
      id: "Zcidy7py-xY",
      lengthS: 37,
    },
    {
      title: "Total to pay, add commission & view fare rules",
      description:
        "Find out how to view booking balances, fare rules and add fees and commissions.",
      id: "pB05rIT8N3I",
      lengthS: 63,
    },
    {
      title: "Confirm a booking",
      description:
        "Find out how to make a payment using your agency card and confirm a booking in Junction Hub.",
      id: "OQMqh6fCczo",
      lengthS: 69,
    },
    {
      title: "Check order status",
      description:
        "Find out how to view all of your existing orders, check their status and download your customers’ tickets in Junction Hub.",
      id: "2ZHcdPvcJ-U",
      lengthS: 47,
    },
  ];

  function getDuration(lengthS: number): string {
    const minutes = Math.floor(lengthS / 60);
    const seconds = lengthS % 60;

    return [minutes ? `${minutes}m` : undefined, seconds ? `${seconds}s` : undefined]
      .filter(ensureDefined)
      .join(" ");
  }
</script>

<script lang="ts">
  import StandardLayout from "components/page/standard-layout.svelte";
  import VideoPlayer, { type YouTubeVideo } from "./video-player.svelte";
  import PlayIcon from "components/icons/play-icon.svelte";
  import { ensureDefined } from "utils/array";
  import ClockIcon from "components/icons/clock-icon.svelte";

  let videoPlayer: VideoPlayer | undefined;
</script>

<svelte:head>
  <title>Knowledge Hub · Junction Hub</title>
</svelte:head>

<VideoPlayer bind:this={videoPlayer} />

<StandardLayout pageTitle="Knowledge Hub" backgroundImage="none">
  <section>
    <h2 class="typography headline-small bold">Video Tutorials</h2>
    <p class="typography title-medium">
      Get to know Junction Hub in just a few minutes with our quick video tutorials.
    </p>

    <div class="videos">
      {#each videos as video}
        {@const action = videoPlayer?.open.bind(videoPlayer.open, video)}

        <div class="video">
          <button
            style:background-image="url(https://img.youtube.com/vi/{video.id}/mqdefault.jpg)"
            on:click={action}
          >
            <PlayIcon variant="circle" />
          </button>

          <span class="action typography body-medium">
            <ClockIcon variant="outlined" />
            {getDuration(video.lengthS)}
          </span>

          <div class="info">
            <h3 class="typography title-large bold">{video.title}</h3>
            <p class="typography body-large">
              {video.description}
            </p>
          </div>
        </div>
      {/each}
    </div>
  </section>
</StandardLayout>

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

  .video {
    display: flex;
    flex-flow: column;
    gap: 24px;
    padding: 0 0 24px;
    overflow: hidden;
    background-color: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .video > button {
    display: flex;
    flex-flow: column;
    align-items: center;
    justify-content: center;
    height: 190px;
    padding: 0;
    background-repeat: no-repeat;
    background-size: cover;
    border: 0;
    cursor: pointer;
  }

  .action {
    display: flex;
    gap: 8px;
    align-items: center;
    align-self: flex-start;
    height: 32px;
    margin: 0 24px;
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
    padding: 0 24px;
  }

  .info > p {
    color: var(--color-common-light-medium);
  }
</style>
