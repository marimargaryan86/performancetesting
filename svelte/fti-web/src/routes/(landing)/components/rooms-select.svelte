<script lang="ts">
  import CountIncrement from "components/count-increment.svelte";
  import type { Room } from "models/common";

  let roomCount: number = 1;

  export let rooms: Room[] = [
    {
      adults: 1,
      children: 1,
    },
  ];

  $: rooms = Array.from({ length: roomCount }, () => ({
    adults: 1,
    children: 1,
  }));
</script>

<div class="dropdown">
  <div class="room-counter">
    <p>Rooms</p>
    <CountIncrement bind:value={roomCount} />
  </div>
  {#each rooms as room, i}
    <div class="room-heading">
      <p>Room {i + 1}</p>
    </div>
    <div class="passenger-selection">
      <div class="passenger-type">
        <p>Adults</p>
      </div>
      <CountIncrement bind:value={room.adults} />
    </div>
    <div class="passenger-selection">
      <div class="passenger-type">
        <p>Children</p>
      </div>
      <CountIncrement bind:value={room.children} />
    </div>
  {/each}
  <!-- Change to new button designs at bottom -->
  <!-- <div class="apply-container">
    <button class="apply">Apply</button>
  </div> -->
</div>

<style>
  .dropdown {
    position: absolute;
    box-shadow: 0px 0px 29.7px 0px rgba(0, 0, 0, 0.1);
    background: #fff;
    top: 110px;
    display: flex;
    flex-direction: column;
    left: -36px;
    width: 150%;
    padding: 32px;
  }

  .passenger-selection {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
  }

  .passenger-type p {
    color: var(--text-dark-text, #1c1c1c);
    font-size: 16px;
    font-style: normal;
    font-weight: 400;
    line-height: normal;
  }

  .room-counter {
    display: flex;
    justify-content: space-between;
  }

  .room-counter p {
    color: var(--text-dark-text, #1c1c1c);
    font-size: 18px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
  }

  .room-heading {
    color: var(--text-dark-text, #1c1c1c);
    font-size: 16px;
    font-style: normal;
    font-weight: 600;
    line-height: normal;
    border-bottom: 1px solid #f2f2f2;
  }
  /*
  .apply-container {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }

  .apply {
    width: 100%;
    background: var(--text-dark-text, #1c1c1c);
    color: white;
    border: none;
    height: 61px;
    padding: 10px;
    justify-content: center;
    align-items: center;
  } */
</style>
