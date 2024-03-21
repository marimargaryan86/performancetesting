<script lang="ts">
  import { database } from "$lib/data/database";

  const { keyReasons } = database;
</script>

<div class="key-features-container">
  <h3>Key Features</h3>
  <span class="key-features-heading"> Why you should book with us? </span>
  <img src="/icons/big-xtra-swipe.svg" alt="Big Xtra " />
  <div class="reason-cards">
    {#each keyReasons as reason}
      <div class="reason-card">
        <div class="reason-card-icon">
          <img src={`/icons/${reason.icon}`} alt={reason.title} />
        </div>
        <div class="reason-content">
          <div class="reason-title">{reason.title}</div>
          <div class="reason-desc">{reason.description}</div>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .key-features-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
    padding: 60px 76px;
    color: white;
    background: #00a8cd;
  }

  h3 {
    margin: 0;
  }

  .key-features-heading {
    width: 75%;
    font-weight: 600;
    font-size: 26px;
    font-style: normal;
    line-height: 44px;
    text-align: center;
  }

  .reason-cards {
    display: flex;
    flex-direction: row;
    gap: 20px;
    align-items: center;
    justify-content: center;
  }

  .reason-card {
    display: flex;
    gap: 16px;
    padding: 32px 14px;
    color: var(--text-dark-text);
    background: #ffffff;
    border-radius: 8px;
  }

  .reason-title {
    margin-bottom: 8px;
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 18px;
    text-transform: capitalize;
  }

  .reason-desc {
    color: #818181;
    font-weight: 400;
    font-size: 15px;
    line-height: 24px;
  }

  @media only screen and (width <= 720px) {
    .key-features-container {
      padding: 48px 0;
    }

    .reason-cards {
      flex-direction: column;
      gap: 16px;
      padding: 0 20px;
    }

    .reason-card {
      align-items: center;
      padding: 24px 32px;
    }
  }
</style>
