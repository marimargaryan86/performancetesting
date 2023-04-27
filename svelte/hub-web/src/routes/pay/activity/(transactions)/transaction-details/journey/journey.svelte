<script lang="ts">
  import Trip from "./trip.svelte";

  const data = {
    outbound: {
      operator: "Air France",
      class: "Economy",
      departureAt: new Date(),
      arrivalAt: new Date(),
      duration: 7500,
      origin: "London Heathrow",
      destination: "Charles de Gaulle",
      equipment: "Air France 319",
    },
    inbound: {
      operator: "Air France",
      class: "Premium Economy",
      departureAt: new Date(),
      arrivalAt: new Date(),
      duration: 7500,
      origin: "Charles de Gaulle",
      destination: "London Heathrow",
      equipment: "Air France 319",
    },
  };
</script>

<div class="journey">
  <h3 class="typography title-medium bold">Trip</h3>

  <div class="content">
    <Trip data={data.outbound} direction="Departure" />

    <hr />

    <Trip data={data.inbound} direction="Return" />
  </div>
</div>

<style>
  .journey {
    display: flex;
    flex-flow: column;
    gap: 24px;
    max-height: 320px;
    padding: 24px;
    overflow: hidden;
    color: var(--color-common-light-strong);
    border: var(--color-main-neutral-200) 1px solid;
    border-radius: 16px;
  }

  .content {
    flex-grow: 1;
    margin: 0 -24px -24px;
    padding: 0 24px 24px;
    overflow: auto;
  }

  hr {
    margin: 24px 0;
    border: 0;
    border-bottom: var(--color-main-neutral-400) 1px solid;
  }
</style>
