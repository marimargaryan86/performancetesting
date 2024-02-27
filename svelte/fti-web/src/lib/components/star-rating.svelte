<script lang="ts">
  import FaStar from "svelte-icons/fa/FaStar.svelte";
  export const starRating: number = 0;
</script>

<div class="stars-container">
  {#each Array.from({ length: 5 }, (_, i) => i + 1) as star}
    <div class="star" data-star={star}>
      <FaStar />
    </div>
  {/each}
</div>

<style>
  .stars-container {
    display: flex;
    margin: 16px 0;
  }

  .star {
    width: 22px;
    color: #fbd148;
  }
</style>
