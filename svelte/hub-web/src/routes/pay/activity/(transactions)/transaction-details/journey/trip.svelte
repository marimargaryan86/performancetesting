<script lang="ts">
  import FlightIcon from "components/icons/flight-icon.svelte";
  import EntityAvatar from "components/ui/entity-avatar.svelte";
  import { formatDuration } from "formatting/date-time";

  export let data: {
    operator: string;
    class: string;
    departureAt: Date;
    arrivalAt: Date;
    duration: number;
    origin: string;
    destination: string;
    equipment: string;
  };
  export let direction: string;
</script>

<div class="trip">
  <span class="typography body-small departure">
    <FlightIcon color="var(--color-main-primary-900)" />

    {direction} • {data.departureAt.toLocaleDateString("en-GB", {
      weekday: "long",
      day: "numeric",
      month: "long",
    })}
  </span>

  <span class="info">
    <span class="typography body-medium operator">
      <EntityAvatar name={data.operator} size="24px" />
      {data.operator}
    </span>

    <span class="typography body-small class">{data.class}</span>
    <span class="typography body-small duration">{formatDuration(data.duration)}</span>
  </span>

  <div class="stops">
    <span class="point" />
    <span class="typography body-medium bold">{data.origin}</span>
    <span class="typography body-medium time">
      {data.departureAt.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
      })}
    </span>

    <span class="line" />
    <span class="typography body-small equipment">{data.equipment}</span>

    <span class="point" />
    <span class="typography body-medium bold">{data.destination}</span>
    <span class="typography body-medium time">
      {data.arrivalAt.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
      })}
    </span>
  </div>
</div>

<style>
  .trip {
    display: flex;
    flex-flow: column;
    gap: 16px;
  }

  .departure {
    display: flex;
    gap: 12px;
    align-items: center;
    color: var(--color-main-neutral-700);
  }

  .info {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .operator {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .operator > :global(svg) {
    flex-shrink: 0;
  }

  .class {
    flex-grow: 1;
  }

  .stops {
    display: grid;
    grid-template-columns: 24px 1fr max-content;
    gap: 2px;
    align-items: center;
  }

  .point {
    display: block;
    justify-self: center;
    width: 9px;
    height: 9px;
    border: var(--color-main-primary-900) 1px solid;
    border-radius: 50%;
  }

  .line {
    display: block;
    justify-self: center;
    width: 0;
    height: 100%;
    border: var(--color-main-primary-900) 1px solid;
  }

  .time {
    color: var(--color-main-neutral-700);
  }

  .equipment {
    grid-column: 2 / -1;
    color: var(--color-main-neutral-500);
  }
</style>
