<script lang="ts">
  import CountIncrement from "$lib/components/count-increment.svelte";
  import type { Room } from "$lib/models/common";

  let roomCount: number = 1;

  export let rooms: Room[] = [
    {
      adults: 1,
      children: 1,
    },
  ];

  function dismiss(): void {
    // coming soon. I don't want to bubble really and im unsure where to go
  }

  function adjustRooms(): void {
    if (roomCount > rooms.length) {
      rooms = [
        ...rooms,
        {
          adults: 1,
          children: 1,
        },
      ];
    } else if (roomCount < rooms.length) {
      rooms = rooms.slice(0, roomCount);
    }
  }

  $: roomCount, adjustRooms();

  // $: {
  //   if (roomCount > rooms.length) {
  //     rooms = [
  //       ...rooms,
  //       {
  //         adults: 1,
  //         children: 1,
  //       },
  //     ];
  //   } else if (roomCount < rooms.length) {
  //     rooms = rooms.slice(0, roomCount);
  //   }
  // }
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
  <div class="apply-container">
    <button class="apply" on:click={dismiss}>Apply</button>
  </div>
</div>

<style>
  .dropdown {
    position: absolute;
    top: 120px;
    left: -36px;
    display: flex;
    flex-direction: column;
    width: 100%;
    padding: 32px;
    background: #ffffff;
    box-shadow: 0 0 29.7px 0 rgb(0 0 0 / 0.1);
  }

  .passenger-selection {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
  }

  .passenger-type p {
    color: var(--text-dark-text);
    font-weight: 400;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
  }

  .room-counter {
    display: flex;
    justify-content: space-between;
  }

  .room-counter p {
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 18px;
    font-style: normal;
    line-height: normal;
  }

  .room-heading {
    color: var(--text-dark-text);
    font-weight: 600;
    font-size: 16px;
    font-style: normal;
    line-height: normal;
    border-bottom: 1px solid #f2f2f2;
  }
</style>
