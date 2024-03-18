<script lang="ts">
  import Icon from "./icon.svelte";

  export const starRating: number = 0;
</script>

<div class="stars-container">
  {#each Array.from({ length: 5 }, (_, i) => i + 1) as star}
    <div class="star" data-star={star}>
      <Icon variant="star" color="gold" />
    </div>
  {/each}
</div>

<style>
  .stars-container {
    display: flex;
    margin: 16px 0;
  }

  .star {
    width: 20px;
  }

  :global(.star > svg) {
    color: #fbd148;
  }
</style>
