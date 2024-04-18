<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import Icon from "$lib/components/icon.svelte";

  export let images: string[] = [];
  export let isOpen = false;
  export let initialIndex = 0;
  let selectedIndex = initialIndex;

  interface DispatchEvents {
    close: undefined;
  }

  const dispatch = createEventDispatcher<DispatchEvents>();

  function closeModal() {
    dispatch("close");
  }

  function navigate(direction: number) {
    const newIndex = selectedIndex + direction;
    if (newIndex >= 0 && newIndex < images.length) {
      selectedIndex = newIndex;
    }
  }

  function selectImage(index: number) {
    selectedIndex = index;
  }
</script>

{#if isOpen}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="modal-overlay" on:click={closeModal}>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="modal-container" on:click|stopPropagation>
      <button class="close-btn" on:click={closeModal}>X</button>
      <div class="modal-content">
        <button class="nav-btn left" on:click={() => navigate(-1)} disabled={selectedIndex === 0}>
          <Icon variant="back-icon" size="50px" color="gray" />
        </button>
        <img src={images[selectedIndex]} alt={`Image ${selectedIndex + 1} of ${images.length}`} />
        <button
          class="nav-btn right"
          on:click={() => navigate(1)}
          disabled={selectedIndex === images.length - 1}
        >
          <Icon variant="forward-icon" size="50px" color="gray" />
        </button>
      </div>
      <p class="image-counter">{selectedIndex + 1} / {images.length}</p>
      <div class="thumbnails">
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        {#each images as image, index}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
          <img
            class:selected={index === selectedIndex}
            src={image}
            alt={`Thumbnail ${index + 1}`}
            on:click={() => selectImage(index)}
          />
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .modal-container {
    position: relative;
    width: fit-content;
    margin: auto;
  }

  .modal-content {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .nav-btn {
    font-size: 24px;
    border: none;
    background: none;
    cursor: pointer;
    padding: 0 20px;
    color: #ffffff;
  }

  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
  }

  .nav-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    user-select: none;
  }

  img {
    max-width: 90vw;
    max-height: 80vh;
    object-fit: contain;
    margin-bottom: 10px;
  }

  .thumbnails {
    display: flex;
    overflow-x: auto;
    padding: 10px;
    gap: 5px;
  }

  .thumbnails img {
    cursor: pointer;
    width: 50px;
    height: 50px;
    object-fit: cover;
    opacity: 0.6;
    transition: opacity 0.3s ease;
  }

  .thumbnails img.selected {
    opacity: 1;
    outline: 2px solid blue;
  }

  img {
    height: auto;
    max-height: 80vh;
    max-width: 90vw;
  }

  .image-counter {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    color: #ffffff;
    font-size: 16px;
  }
</style>
