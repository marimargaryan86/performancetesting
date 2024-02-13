<div class="filter-buttons">
  <button class="filter-button">
    <div class="icon">
      <img src="/icons/chevron-left.svg" alt="Chevron Left" />
    </div>
  </button>
  <button class="filter-button">
    <div class="icon">
      <img src="/icons/chevron-right.svg" alt="Chevron Right" />
    </div>
  </button>
</div>

<style>
  .filter-buttons {
    display: flex;
    gap: 8px;
  }

  .filter-button {
    border-radius: 50%;
    padding: 0;
    border: 1px solid black;
    height: 32px;
    background: none;
  }

  .filter-button .icon {
    width: 30px;
    height: 30px;
    position: relative;
  }

  .filter-button .icon img {
    width: 18px;
    height: 28px;
    position: absolute;
    left: 0;
    padding: 2px 6px;
  }
</style>
